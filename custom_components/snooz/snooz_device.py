import asyncio
import logging
from threading import RLock
from datetime import datetime
from bluepy import btle

from .const import (
    DOMAIN,
    CONF_ADDRESS,
    SNOOZ_SERVICE_UUID,
    READ_STATE_UUID,
    WRITE_STATE_UUID,
    CONNECTION_SEQUENCE,
    STATE_UPDATE_LENGTH,
    COMMAND_TURN_ON,
    COMMAND_TURN_OFF,
    CONNECTION_RETRY_INTERVAL,
    NOTIFICATION_TIMEOUT,
    MAX_QUEUED_STATE_AGE
)

_LOGGER = logging.getLogger(__name__)

class SnoozeDevice():
    on = False
    level = 1
    connected = False

    _running = False
    _sleep_task = None
    _on_state_change = None
    _state_lock = None
    _sleep_lock = None
    _queued_state = []

    def __init__(self, loop, on_state_change):
        self._state_lock = RLock()
        self._sleep_lock = RLock()

        self.loop = loop

        self._on_state_change = on_state_change
        self._device = btle.Peripheral()

    def stop(self):
        self._running = False

        if self.connected and self._device:
            try:
                self._device.disconnect()
            except:
                pass

        self._cancel_sleep()
    
    def start(self, address: str):
        self._running = True
        self.loop.create_task(self._async_run(address))
    
    async def _async_run(self, address: str):
        while True:
            if not self._running:
                return
            try:
                if self.connected:
                    self._flush_queued_state()
                    self._update_state()
                else:
                    self._device.connect(address)
                    self._init_connection()
            except btle.BTLEDisconnectError:
                self._on_disconnected()
            finally:
                self._flush_queued_state()
                await self._sleep()

    def set_on(self, on: bool):
        self._write_state(COMMAND_TURN_ON if on else COMMAND_TURN_OFF)

    def set_level(self, level: int):
        if level < 1 or level > 10:
            raise Exception("Invalid level {}".format(level))

        self._write_state([0x01, level * 10])

    def queue_state(self, state_writer: callable):
        with self._state_lock:
            self._queued_state.append((datetime.now(), state_writer))
        
        self._cancel_sleep()

    def _flush_queued_state(self):
        while self.connected:
            task = None

            with self._state_lock:
                now = datetime.now()

                # remove stale jobs
                self._queued_state = [
                    (created, task) for (created, task) in self._queued_state 
                    if (now - created).seconds <= MAX_QUEUED_STATE_AGE
                ]

                if len(self._queued_state) == 0:
                    return

                (_, task) = self._queued_state[0]
            
            if task:
                task()

            if self.connected:
                with self._state_lock:
                    self._queued_state.pop(0)
    def _init_connection(self):
        self.connected = True

        service = self._device.getServiceByUUID(SNOOZ_SERVICE_UUID)

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

        if was_connected:
            self._on_state_change()

    async def _sleep(self):
        seconds = NOTIFICATION_TIMEOUT if self.connected else CONNECTION_RETRY_INTERVAL

        with self._state_lock:
            # use a small timeout when we have queued jobs
            if len(self._queued_state) > 0:
                seconds = 0.5
        
        with self._sleep_lock:
            self._sleep_task = self.loop.create_task(asyncio.sleep(seconds))
        try:
            await self._sleep_task
        except asyncio.CancelledError:
            pass
        with self._sleep_lock:
            self._sleep_task = None
    
    def _cancel_sleep(self):
        with self._sleep_lock:
            if self._sleep_task:
                self._sleep_task.cancel()
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