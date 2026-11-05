"""The BLE client must recover from a Bluetooth proxy that stops answering."""

import asyncio

import pytest

pytest.importorskip("bleak_retry_connector")

from pixel_clock import device  # noqa: E402


class _Client:
    is_connected = True
    mtu_size = 517

    def __init__(self, disconnect):
        self._disconnect = disconnect

    async def disconnect(self):
        await self._disconnect()


def _panel(disconnect):
    panel = device.PixelClockClient("test", lambda: None)
    panel._client = _Client(disconnect)
    return panel


def test_disconnect_error_does_not_escape():
    async def fails():
        raise TimeoutError("no response from the proxy")

    async def run():
        panel = _panel(fails)
        await panel.async_disconnect()
        assert panel._client is None
        assert not panel.connected
        await panel.async_disconnect()  # nothing left to do

    asyncio.run(run())


def test_disconnect_that_hangs_is_given_up(monkeypatch):
    monkeypatch.setattr(device, "DISCONNECT_TIMEOUT", 0.01)

    async def hangs():
        await asyncio.Event().wait()

    async def run():
        panel = _panel(hangs)
        await panel.async_disconnect()
        assert panel._client is None
        assert not panel._lock.locked()

    asyncio.run(run())


def test_operation_that_hangs_times_out_and_frees_the_lock(monkeypatch):
    monkeypatch.setattr(device, "COMMAND_TIMEOUT", 0.01)

    async def hangs(_ble_device):
        await asyncio.Event().wait()

    async def run():
        panel = device.PixelClockClient("test", lambda: None)
        panel._ensure_connected = hangs
        with pytest.raises(TimeoutError):
            await panel.async_command(None, b"x")
        assert not panel._lock.locked()

    asyncio.run(run())


def test_cancelling_during_disconnect_still_cancels():
    async def hangs():
        await asyncio.Event().wait()

    async def run():
        panel = _panel(hangs)
        task = asyncio.create_task(panel.async_disconnect())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
