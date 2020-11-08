import asyncio
import logging
from bluepy import btle

from .const import (
    DOMAIN,
    CONF_ADDRESS,
    SERVICE_UUID,
    READ_STATE_UUID,
    WRITE_STATE_UUID,
    CONNECTION_SEQUENCE,
    STATE_UPDATE_LENGTH,
    COMMAND_TURN_ON,
    COMMAND_TURN_OFF,
    CONNECTION_RETRY_INTERVAL,
    NOTIFICATION_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)

class SnoozeDevice():
    on = False
    level = 0
    connected = False

    _running = False
    _sleep_task = None
    _on_state_change = None

    def __init__(self, loop, on_state_change):
        self.loop = loop

        self._on_state_change = on_state_change
        self._device = btle.Peripheral()

    def start(self, address: str):
        self._running = True
        self.loop.create_task(self._async_run(address))

    def stop(self):
        self._running = False

        if self._sleep_task:
            self._sleep_task.cancel()
            self._sleep_task = None
        
        if self.connected and self._device:
            try:
                self._device.disconnect()
            except:
                pass

    async def _async_run(self, address: str):
        while True:
            if not self._running:
                return
            try:
                if self.connected:
                    self._update_state()
                else:
                    self._device.connect(address)
                    self._init_connection()
            except btle.BTLEDisconnectError:
                self._on_disconnected()
            finally:
                self._sleep(NOTIFICATION_TIMEOUT if self.connected else CONNECTION_RETRY_INTERVAL)

    def set_on(self, on: bool):
        self._write_state(COMMAND_TURN_ON if on else COMMAND_TURN_OFF)
        self._update_state()

    def set_level(self, level: int):
        if level < 1 or level > 10:
            raise Exception("Invalid level {}".format(level))

        self._write_state([0x01, level * 10])
        self._update_state()

    def _init_connection(self):
        self.connected = True

        service = self._device.getServiceByUUID(SERVICE_UUID)

        self._reader = service.getCharacteristics(READ_STATE_UUID)[0]
        self._writer = service.getCharacteristics(WRITE_STATE_UUID)[0]

        for bytes in CONNECTION_SEQUENCE:
            self._write_state(bytes)

        # load initial state
        self._update_state()
        
    def _on_disconnected(self):
        was_connected = self.connected

        self.connected = False
        self._reader = None
        self._writer = None

        # notify unavailable
        if was_connected:
            self._on_state_change()

    def _sleep(self, seconds: int):
        self._sleep_task = self.loop.create_task(asyncio.sleep(seconds))
        try:
            await self._sleep_task
        except asyncio.CancelledError:
            pass
        self._sleep_task = None
    
    def _update_state(self):
        if self.connected and self._reader:
            try:
                self._on_receive_state(self._reader.read())
            except:
                self._on_disconnected()
        
    def _on_receive_state(self, data: bytearray):
        # malformed or unexpected data
        if len(data) != STATE_UPDATE_LENGTH:
            return
        
        on = data[1] == 0x01
        level = int(data[0] / 10)

        # state not changed
        if on == self.on and level == self.level:
            return

        self.on = on
        self.level = level

        self._on_state_change()

    def _write_state(self, state: list):
        if self._writer == None:
            return
        try:
            self._writer.write(bytearray(state), withResponse=True)
        except:
            self._on_disconnected()