import asyncio
import logging
from datetime import datetime
from threading import RLock

import bluepy.btle
from .bluetooth_peripheral import PeripheralWithConnectTimeout

from .const import (COMMAND_TURN_OFF, COMMAND_TURN_ON, CONNECTION_TIMEOUT,
                   CONNECTION_RETRY_INTERVAL, CONNECTION_SEQUENCE,
                   MAX_QUEUED_STATE_AGE, MAX_QUEUED_STATE_COUNT, NOTIFICATION_TIMEOUT, READ_STATE_UUID,
                   SNOOZ_SERVICE_UUID, STATE_UPDATE_LENGTH, WRITE_STATE_UUID)

class SnoozeDevice():
    on = False
    percentage = 0
    connected = False

    _running = False
    _run_task = None
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
        self._device = PeripheralWithConnectTimeout()

    def stop(self):
        self._running = False

        if self._run_task is not None and not self._run_task.cancelled():
            self._run_task.cancel()
            self._run_task = None

        if self.connected and self._device:
            try:
                self._device.disconnect()
            except:
                pass

        self._cancel_sleep()

    def start(self, address: str):
        self._running = True
        self._run_task = self.loop.create_task(self._async_run(address))

    async def _async_run(self, address: str):
        while True:
            if not self._running:
                return
            try:
                if self.connected:
                    self._flush_queued_state()
                    self._update_state()
                else:
                    self._device.connect(address, timeout=CONNECTION_TIMEOUT)
                    self._init_connection()
            except bluepy.btle.BTLEDisconnectError:
                self._on_disconnected()
            finally:
                self._flush_queued_state()
                await self._sleep()

    def set_on(self, on: bool):
        self._write_state(COMMAND_TURN_ON if on else COMMAND_TURN_OFF)

    def set_percentage(self, percentage: int):
        if percentage < 0 or percentage > 100:
            raise Exception("Invalid percentage {}".format(percentage))

        self._write_state([0x01, percentage])

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
                queued_state = [
                    (created, task) for (created, task) in self._queued_state
                    if (now - created).seconds <= MAX_QUEUED_STATE_AGE
                ][-MAX_QUEUED_STATE_COUNT:]

                if len(queued_state) == 0:
                    return

                (_, task) = queued_state[0]
                self._queued_state = queued_state

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
        percentage = data[0]

        # state not changed
        if on == self.on and percentage == self.percentage:
            return

        self.on = on
        self.percentage = percentage

        self._on_state_change()

    def _write_state(self, state: list):
        if self._writer == None:
            return
        try:
            self._writer.write(bytearray(state), withResponse=True)
        except:
            self._on_disconnected()
