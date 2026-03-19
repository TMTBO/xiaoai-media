from __future__ import annotations

import asyncio
import json
import logging
import time
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
            _log.debug("MiService: using passToken auth for user %s", config.MI_USER)
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
            _log.debug(
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

        _log.debug(
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
                _log.debug(
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
                    _log.debug(
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

        Uses play_by_music_url method which uses the player_play_music API.
        This method is more reliable for most Xiaomi speaker hardware.

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
            "MiService: play URL on device %s (hardware=%s, type=%d)", 
            did, hardware, _type
        )
        _log.debug("Full URL: %s", url)

        try:
            # Ensure device hardware mapping is initialized
            if not hasattr(self._na_service, 'device2hardware') or not self._na_service.device2hardware:
                _log.debug("Initializing device hardware mapping...")
                if not hasattr(self._na_service, 'device2hardware'):
                    self._na_service.device2hardware = {}
                for d in devices:
                    dev_id = d.get("deviceID")
                    hw = d.get("hardware")
                    if dev_id and hw:
                        self._na_service.device2hardware[dev_id] = hw
                _log.debug("Device hardware mapping: %s", self._na_service.device2hardware)

            # Use play_by_music_url for better compatibility
            audio_id = "1582971365183456177"
            cp_id = "355454500"
            
            _log.info("Calling play_by_music_url with audio_id=%s, cp_id=%s", audio_id, cp_id)
            
            result = await self._na_service.play_by_music_url(
                did, url, _type, audio_id, cp_id
            )
            _log.info("MiService: play_by_music_url result: %s", result)
            
            # Check if the result indicates success
            success = False
            if isinstance(result, dict):
                # Check nested code structure: result.data.code or result.code
                data_code = result.get("data", {}).get("code") if isinstance(result.get("data"), dict) else None
                result_code = result.get("code")
                success = (data_code == 0) or (result_code == 0)
                _log.info("Result codes: result.code=%s, result.data.code=%s, success=%s", 
                          result_code, data_code, success)
            
            return {
                "device": f"{device_name}({did})",
                "url": url,
                "result": success,
                "hardware": hardware,
                "raw_result": result,
            }
        except Exception as e:
            _log.error("MiService: play_url failed: %s", e, exc_info=True)
            raise

    async def get_latest_ask(self, device_id: str | None = None, limit: int = 2) -> list[dict]:
        """Get latest conversation records from the speaker.

        Args:
            device_id: Target device ID (optional)
            limit: Maximum number of records to fetch (default: 2)

        Returns a list of conversation records with query, answer, and timestamp.
        Uses the Xiaomi conversation API directly.
        """
        did = await self._resolve_device_id(device_id)

        # Get device hardware for API request
        devices = await self.list_devices()
        hardware = None
        for device in devices:
            if device["deviceID"] == did:
                hardware = device.get("hardware", "")
                break

        if not hardware:
            _log.warning("Cannot find hardware for device %s, using default", did)
            hardware = "LX06"

        # Get serviceToken and userId from MiAccount or .mi.token file
        # Ensure we're logged in first
        assert self._na_service is not None
        await self._na_service.device_list()  # This triggers login if needed
        
        service_token = None
        user_id = None
        
        # Try to get from MiAccount first
        if self._account and self._account.token:
            token_data = self._account.token
            service_token = token_data.get("serviceToken")
            user_id = token_data.get("userId")
        
        # If serviceToken not in MiAccount, read from .mi.token file
        if not service_token:
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            token_file = os.path.join(project_root, ".mi.token")
            
            try:
                if os.path.exists(token_file):
                    with open(token_file, "r") as f:
                        token_data = json.load(f)
                        if not user_id:
                            user_id = token_data.get("userId")
                        micoapi = token_data.get("micoapi", [])
                        if len(micoapi) > 1:
                            service_token = micoapi[1]
                            _log.debug("Loaded serviceToken from .mi.token file")
            except Exception as e:
                _log.warning("Failed to read .mi.token: %s", e)
        
        _log.debug("Auth info: userId=%s, has_serviceToken=%s", user_id, bool(service_token))
        
        if not service_token or not user_id:
            _log.warning("No valid serviceToken or userId available for conversation API")
            return []

        # Use Xiaomi conversation API
        timestamp = int(time.time() * 1000)
        url = f"https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit={limit}"

        _log.debug("MiService: get latest ask from device %s (hardware: %s)", did, hardware)

        try:
            assert self._session is not None

            # Build cookies manually
            cookies = {"deviceId": did}
            if service_token:
                cookies["serviceToken"] = service_token
            if user_id:
                cookies["userId"] = str(user_id)

            _log.debug("Request cookies: deviceId=%s, has_serviceToken=%s, userId=%s", 
                      did, bool(service_token), user_id)

            async with self._session.get(url, cookies=cookies, timeout=15) as resp:
                if resp.status != 200:
                    _log.debug("Conversation API returned status %d", resp.status)
                    if resp.status == 401:
                        _log.debug("Authentication failed, serviceToken may be invalid")
                    elif resp.status == 400:
                        _log.debug("Bad request, check deviceId and hardware parameters")
                    return []

                data = await resp.json()
                _log.debug("Conversation API response: %s", data)

                # Parse response
                result = []
                if d := data.get("data"):
                    records = json.loads(d).get("records", [])
                    for record in records:
                        try:
                            answers = record.get("answers", [{}])
                            answer = ""
                            if answers:
                                answer = (
                                    answers[0].get("tts", {}).get("text", "").strip()
                                )

                            result.append(
                                {
                                    "time": record.get("time", 0),
                                    "query": record.get("query", "").strip(),
                                    "answer": answer,
                                }
                            )
                        except Exception as e:
                            _log.warning("Failed to parse conversation record: %s", e)
                            continue

                return result

        except Exception as e:
            _log.error("MiService: get_latest_ask failed: %s", e, exc_info=True)
            return []

    async def player_pause(self, device_id: str | None = None) -> dict:
        """Pause current playback.

        Uses the player_play_operation API from miservice_fork.
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: pause playback on device %s", did)
        result = await self._na_service.player_pause(did)
        _log.info("MiService: pause result: %s", result)
        return {"device": f"{device_name}({did})", "result": result}

    async def player_stop(self, device_id: str | None = None) -> dict:
        """Stop current playback.

        Uses the player_play_operation API from miservice_fork.
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: stop playback on device %s", did)
        result = await self._na_service.player_stop(did)
        _log.info("MiService: stop result: %s", result)
        return {"device": f"{device_name}({did})", "result": result}

    async def player_play(self, device_id: str | None = None) -> dict:
        """Resume/play current playback.

        Uses the player_play_operation API from miservice_fork.
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: resume playback on device %s", did)
        result = await self._na_service.player_play(did)
        _log.info("MiService: play result: %s", result)
        return {"device": f"{device_name}({did})", "result": result}

    async def player_get_status(self, device_id: str | None = None) -> dict:
        """Get current player status.

        Uses the player_get_play_status API from miservice_fork.
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: get player status on device %s", did)
        result = await self._na_service.player_get_status(did)
        _log.info("MiService: player status result: %s", result)
        return {"device": f"{device_name}({did})", "status": result}

    async def player_set_loop(self, device_id: str | None = None, loop_type: int = 1) -> dict:
        """Set loop mode for playback.

        Args:
            device_id: Target device ID
            loop_type: 0=single track loop, 1=playlist loop (default)
        """
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        devices = await self.list_devices()
        device_name = next(
            (d.get("name", "") for d in devices if d["deviceID"] == did), ""
        )
        _log.info("MiService: set loop mode %d on device %s", loop_type, did)
        result = await self._na_service.player_set_loop(did, loop_type)
        _log.info("MiService: set loop result: %s", result)
        return {"device": f"{device_name}({did})", "loop_type": loop_type, "result": result}




