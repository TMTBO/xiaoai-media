from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientSession

from miservice import MiAccount, MiIOService, MiNAService

from xiaoai_media import config

_log = logging.getLogger(__name__)

# TTS command mapping: hardware short code → "siid-aiid" for miot_action
# Reference: https://github.com/hanxi/xiaomusic/blob/main/xiaomusic/const.py
# These are for TTS播报 (TTS broadcast), which only takes text parameter
TTS_COMMAND = {
    "OH2": "5-3",
    "OH2P": "7-3",
    "LX06": "5-1",
    "S12": "5-1",
    "L15A": "7-3",
    "LX5A": "5-1",
    "LX01": "5-1",
    "LX05": "5-1",
    "X10A": "7-3",
    "L17A": "7-3",
    "ASX4B": "5-3",
    "L06A": "5-1",
    "L05B": "5-3",
    "L05C": "5-3",
    "X6A": "7-3",
    "X08E": "7-3",
    "L09A": "3-1",
    "LX04": "5-1",
}

# Module-level device list cache shared across all client instances (per backend process).
# Populated on first call; cleared by passing force_refresh=True.
_device_cache: list[dict] | None = None


class XiaoAiClient:
    """Async client wrapping MiService for Xiaomi AI speaker control."""

    def __init__(self) -> None:
        self._session: ClientSession | None = None
        self._account: MiAccount | None = None
        self._na_service: MiNAService | None = None
        self._io_service: MiIOService | None = None

    async def __aenter__(self) -> "XiaoAiClient":
        await self.connect()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def connect(self) -> None:
        self._session = ClientSession()
        self._account = MiAccount(
            self._session,
            config.MI_USER,
            config.MI_PASS,
        )
        if config.MI_PASS_TOKEN and config.MI_USER:
            # Pre-inject passToken to allow re-auth without password
            self._account.token = {
                "deviceId": "",
                "userId": config.MI_USER,
                "passToken": config.MI_PASS_TOKEN,
            }
            _log.info("MiService: using passToken auth for user %s", config.MI_USER)
        elif config.MI_USER:
            _log.info("MiService: using password auth for user %s", config.MI_USER)
        else:
            _log.warning("MiService: no credentials configured")
        self._na_service = MiNAService(self._account)
        self._io_service = MiIOService(self._account, region=config.MI_REGION)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Device discovery
    # ------------------------------------------------------------------

    async def list_devices(self, force_refresh: bool = False) -> list[dict]:
        """Return merged device list from MiNAService + MiIOService.

        MiNAService provides: deviceID (UUID for ubus calls), hardware, miotDID.
        MiIOService provides: model (full model name), isOnline, localip, etc.
        Results are cached module-level; pass force_refresh=True to invalidate.
        """
        global _device_cache
        if _device_cache is not None and not force_refresh:
            _log.info(
                "MiService: returning %d device(s) from cache", len(_device_cache)
            )
            return _device_cache

        assert self._na_service is not None
        assert self._io_service is not None
        _log.info("MiService: fetching device list (MiNA + MiIO)")

        mina_result, miio_result = await asyncio.gather(
            self._na_service.device_list(),
            self._io_service.device_list("full"),
            return_exceptions=True,
        )

        if isinstance(mina_result, Exception):
            _log.warning("MiService: MiNAService device_list failed: %s", mina_result)
            mina_result = []
        if isinstance(miio_result, Exception):
            _log.warning("MiService: MiIOService device_list failed: %s", miio_result)
            miio_result = []

        # Index MiIO devices by their numeric did for O(1) lookup
        miio_by_did: dict[str, dict] = {
            str(d["did"]): d for d in (miio_result or []) if "did" in d
        }

        merged: list[dict] = []
        for d in mina_result or []:
            device: dict = dict(d)
            miot_did = str(d.get("miotDID", ""))
            if miot_did and miot_did in miio_by_did:
                miio_d = miio_by_did[miot_did]
                # Enrich with MiIO fields; prefer MiNA values for overlapping keys
                for k, v in miio_d.items():
                    if k not in device:
                        device[k] = v
                # Always take model and connectivity info from MiIO (not in MiNA)
                device["model"] = miio_d.get("model", "")
                device["isOnline"] = miio_d.get("isOnline", False)
                device["localip"] = miio_d.get("localip", "")
            merged.append(device)

        _device_cache = merged
        _log.info("MiService: cached %d merged device(s)", len(merged))
        return _device_cache

    # ------------------------------------------------------------------
    # Speaker control
    # ------------------------------------------------------------------

    async def text_to_speech(self, text: str, device_id: str | None = None) -> dict:
        """Send a TTS broadcast message to the speaker (播报).

        This method uses TTS action (aiid=1 or 3) which only broadcasts text
        without executing commands or expecting device responses.

        Args:
            text: Text to broadcast
            device_id: Target device ID
        """
        # Get device hardware and miotDID
        devices = await self.list_devices()
        hardware = None
        miot_did = None
        device_name = ""
        for device in devices:
            if device["deviceID"] == device_id:
                hardware = device.get("hardware")
                miot_did = device.get("miotDID")
                device_name = device.get("name", "")
                break

        _log.info(
            "MiService: TTS broadcast to device %s (hardware: %s, miotDID: %s): %r",
            device_id,
            hardware,
            miot_did,
            text,
        )

        # Check if hardware has TTS_COMMAND mapping (use miot_action directly)
        if hardware and hardware in TTS_COMMAND:
            assert self._io_service is not None
            if not miot_did:
                _log.warning(
                    "MiService: Device %s has no miotDID, using MiNAService fallback",
                    device_id,
                )
            else:
                tts_cmd = TTS_COMMAND[hardware]  # e.g. "5-1" or "7-3"
                siid, aiid = map(int, tts_cmd.split("-"))
                _log.info(
                    "MiService: miot_action TTS broadcast on device %s (siid=%d, aiid=%d): %r",
                    miot_did,
                    siid,
                    aiid,
                    text,
                )
                try:
                    # TTS broadcast only takes text parameter (no response flag)
                    result = await self._io_service.miot_action(
                        str(miot_did),
                        (siid, aiid),
                        [text],
                    )
                    _log.info("MiService: TTS result (miot_action): %s", result)
                    return {
                        "device": f"{device_name}({device_id})",
                        "miot_did": miot_did,
                        "command": text,
                        "result": result,
                        "method": "miot_action",
                    }
                except Exception as e:
                    _log.warning(
                        "MiService: miot_action failed (%s), trying MiNAService fallback",
                        e,
                    )

        # Fallback to MiNAService text_to_speech
        try:
            assert self._na_service is not None
            _log.info("MiService: Call MiNAService tts")
            result = await self._na_service.text_to_speech(device_id, text)
            _log.info("MiService: TTS result (MiNAService): %s", result)
            return {
                "device": f"{device_name}({device_id})",
                "command": text,
                "result": result,
                "method": "mina_service",
            }
        except Exception as e:
            _log.error("MiService: All TTS methods failed: %s", e, exc_info=True)
            raise

    async def execute_text_command(
        self, text: str, device_id: str | None = None, silent: bool = False
    ) -> dict:
        """Execute a text command on the speaker (执行文本).

        This is equivalent to saying "小爱同学, <text>" to the speaker.
        Uses execute command action (aiid=4) which takes text + response_flag.

        Args:
            text: Command text to execute
            device_id: Target device ID
            silent: If True, execute silently without voice response (default: False)
        """
        # Get device hardware and miotDID
        devices = await self.list_devices()
        hardware = None
        miot_did = None
        device_name = ""
        for device in devices:
            if device["deviceID"] == device_id:
                hardware = device.get("hardware")
                miot_did = device.get("miotDID")
                device_name = device.get("name", "")
                break

        _log.info(
            "MiService: Execute command on device %s (hardware: %s, miotDID: %s, silent: %s): %r",
            device_id,
            hardware,
            miot_did,
            silent,
            text,
        )

        # Reuse TTS_COMMAND for siid; execute action always uses aiid=4
        if hardware and hardware in TTS_COMMAND:
            assert self._io_service is not None
            if not miot_did:
                _log.warning(
                    "MiService: Device %s has no miotDID, using text_to_speech fallback",
                    device_id,
                )
            else:
                siid = int(TTS_COMMAND[hardware].split("-")[0])
                aiid = 4
                # According to MiService docs:
                # micli.py 5-4 查询天气 1  # 1 = voice response enabled
                # micli.py 5-4 关灯 0     # 0 = silent execution
                response_flag = 0 if silent else 1
                _log.info(
                    "MiService: miot_action execute command on device %s (siid=%d, aiid=%d, response=%d): %r",
                    miot_did,
                    siid,
                    aiid,
                    response_flag,
                    text,
                )
                try:
                    # Execute command takes text + response_flag
                    result = await self._io_service.miot_action(
                        str(miot_did),
                        (siid, aiid),
                        [text, response_flag],
                    )
                    _log.info(
                        "MiService: Execute command result (miot_action): %s", result
                    )
                    return {
                        "device": f"{device_name}({device_id})",
                        "miot_did": miot_did,
                        "command": text,
                        "result": result,
                        "method": "miot_action_execute",
                        "silent": silent,
                    }
                except Exception as e:
                    _log.warning(
                        "MiService: miot_action execute failed (%s), trying text_to_speech fallback",
                        e,
                    )

        # Fallback to text_to_speech (TTS broadcast)
        _log.info("MiService: Fallback to text_to_speech")
        return await self.text_to_speech(text, device_id)

    async def _resolve_device_id(self, device_id: str | None) -> str:
        """Return *device_id* if provided, otherwise fall back to config.MI_DID.

        Raises HTTPException(422) if neither is available.
        """
        from fastapi import HTTPException

        if device_id:
            return device_id
        if config.MI_DID:
            return config.MI_DID
        # Try the first available device
        devices = await self.list_devices()
        if devices:
            did = devices[0]["deviceID"]
            _log.info("_resolve_device_id: defaulting to first device %s", did)
            return did
        raise HTTPException(
            status_code=422,
            detail="No device_id provided and MI_DID is not configured",
        )

    async def set_volume(self, volume: int, device_id: str | None = None) -> dict:
        """Set speaker volume (0-100)."""
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: set volume %d on device %s", volume, did)
        result = await self._na_service.player_set_volume(did, volume)
        _log.info("MiService: set volume result: %s", result)
        return {"device": f"{device_name}({did})", "volume": volume, "result": result}
    async def get_volume(self, device_id: str | None = None) -> dict:
        """Get current speaker volume."""
        assert self._io_service is not None
        devices = await self.list_devices()
        did = await self._resolve_device_id(device_id)
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )

        # Get numeric did for miot request
        numeric_did = next(
            (d.get("did", "") for d in devices if d["deviceID"] == did), None
        )
        if not numeric_did:
            raise ValueError(f"Cannot find numeric did for device {did}")

        _log.info("MiService: get volume from device %s (did=%s)", did, numeric_did)
        # Volume is at siid=2 (player service), piid=1 (volume property)
        volume = await self._io_service.miot_get_prop(numeric_did, (2, 1))
        _log.info("MiService: get volume result: %s", volume)

        return {"device": f"{device_name}({did})", "volume": volume}

    async def send_command(
        self, text: str, device_id: str | None = None, silent: bool = False
    ) -> dict:
        """Send a voice command to the speaker (equivalent to saying '小爱同学, <text>').

        This uses execute_text_command which is equivalent to speaking to the device.

        Args:
            text: Command text
            device_id: Target device ID
            silent: If True, execute silently without voice response (default: False)
        """
        _log.info("MiService: send command (silent=%s): %r", silent, text)
        return await self.execute_text_command(text, device_id, silent)

    async def play_url(
        self, url: str, device_id: str | None = None, _type: int = 2
    ) -> dict:
        """Play audio from a URL directly on the speaker.

        Uses the correct method based on hardware type:
        - For certain hardware (OH2P, LX04, etc.): uses player_play_music
        - For other hardware: uses player_play_url

        Args:
            url: Audio URL to play
            device_id: Target device ID
            _type: Play type (1=MUSIC with light on, 2=normal)
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device = next((d for d in devices if d["deviceID"] == did), None)
        if not device:
            raise Exception(f"Device {did} not found")

        device_name = device.get("name", "")
        hardware = device.get("hardware", "")

        _log.info(
            "MiService: play URL on device %s (hardware=%s): %s", did, hardware, url
        )

        # Hardware types that need player_play_music
        USE_PLAY_MUSIC_API = [
            "LX04",
            "LX05",
            "L05B",
            "L05C",
            "L06",
            "L06A",
            "X08A",
            "X10A",
            "X08C",
            "X08E",
            "X8F",
            "X4B",
            "OH2",
            "OH2P",
            "X6A",
        ]

        try:
            if hardware in USE_PLAY_MUSIC_API:
                # Use player_play_music for these hardware types
                _log.info("Using player_play_music for hardware %s", hardware)
                audio_type = "MUSIC" if _type == 1 else ""
                audio_id = "1582971365183456177"
                music = {
                    "payload": {
                        "audio_type": audio_type,
                        "audio_items": [
                            {
                                "item_id": {
                                    "audio_id": audio_id,
                                    "cp": {
                                        "album_id": "-1",
                                        "episode_index": 0,
                                        "id": "355454500",
                                        "name": "xiaowei",
                                    },
                                },
                                "stream": {"url": url},
                            }
                        ],
                        "list_params": {
                            "listId": "-1",
                            "loadmore_offset": 0,
                            "origin": "xiaowei",
                            "type": "MUSIC",
                        },
                    },
                    "play_behavior": "REPLACE_ALL",
                }
                import json

                result = await self._na_service.ubus_request(
                    did,
                    "player_play_music",
                    "mediaplayer",
                    {"startaudioid": audio_id, "music": json.dumps(music)},
                )
                _log.info("MiService: player_play_music result: %s", result)
                return {
                    "device": f"{device_name}({did})",
                    "url": url,
                    "result": (
                        result.get("code") == 0 if isinstance(result, dict) else result
                    ),
                    "method": "player_play_music",
                    "hardware": hardware,
                }
            else:
                # Use player_play_url for other hardware
                _log.info("Using player_play_url for hardware %s", hardware)
                result = await self._na_service.ubus_request(
                    did,
                    "player_play_url",
                    "mediaplayer",
                    {"url": url, "type": _type, "media": "app_ios"},
                )
                _log.info("MiService: player_play_url result: %s", result)
                return {
                    "device": f"{device_name}({did})",
                    "url": url,
                    "result": (
                        result.get("code") == 0 if isinstance(result, dict) else result
                    ),
                    "method": "player_play_url",
                    "hardware": hardware,
                }
        except Exception as e:
            _log.error("MiService: play_url failed: %s", e, exc_info=True)
            raise
