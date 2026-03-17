from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientSession
from miservice import MiAccount, MiIOService, MiNAService

from xiaoai_media import config

_log = logging.getLogger(__name__)


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

    async def list_devices(self) -> list[dict]:
        """Return list of Xiaomi AI speaker devices."""
        assert self._na_service is not None
        _log.info("MiService: fetching device list")
        devices = await self._na_service.device_list()
        _log.info("MiService: found %d device(s)", len(devices))
        return devices

    async def _resolve_device_id(self, device_id: str | None) -> str:
        """Resolve device_id: use provided value, config default, or first device."""
        if device_id:
            return device_id
        if config.MI_DID:
            return config.MI_DID
        devices = await self.list_devices()
        if not devices:
            raise RuntimeError("No Xiaomi AI speaker devices found.")
        return devices[0]["deviceID"]

    # ------------------------------------------------------------------
    # Speaker control
    # ------------------------------------------------------------------

    async def text_to_speech(self, text: str, device_id: str | None = None) -> dict:
        """Send a TTS message to the speaker."""
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        _log.info("MiService: TTS to device %s: %r", did, text)
        result = await self._na_service.text_to_speech(did, text)
        _log.info("MiService: TTS result: %s", result)
        return {"device_id": did, "text": text, "result": result}

    async def set_volume(self, volume: int, device_id: str | None = None) -> dict:
        """Set speaker volume (0-100)."""
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        _log.info("MiService: set volume %d on device %s", volume, did)
        result = await self._na_service.player_set_volume(did, volume)
        _log.info("MiService: set volume result: %s", result)
        return {"device_id": did, "volume": volume, "result": result}

    async def send_command(self, text: str, device_id: str | None = None) -> dict:
        """Send a voice command to the speaker."""
        assert self._na_service is not None
        did = await self._resolve_device_id(device_id)
        _log.info("MiService: send command to device %s: %r", did, text)
        result = await self._na_service.ubus_request(
            did,
            "command",
            "mibrain",
            {"text": text, "respond": 1},
        )
        _log.info("MiService: command result: %s", result)
        return {"device_id": did, "command": text, "result": result}
