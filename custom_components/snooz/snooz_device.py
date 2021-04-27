import asyncio
import logging
from datetime import datetime
import threading
from threading import RLock

import bluepy.btle
from .bluetooth_peripheral import PeripheralWithConnectTimeout

from .const import (COMMAND_TURN_OFF, COMMAND_TURN_ON, CONNECTION_TIMEOUT,
                   CONNECTION_RETRY_INTERVAL, CONNECTION_SEQUENCE,
                   MAX_QUEUED_STATE_AGE, MAX_QUEUED_STATE_COUNT, NOTIFICATION_TIMEOUT, READ_STATE_UUID,
                   SNOOZ_SERVICE_UUID, STATE_UPDATE_LENGTH, WRITE_STATE_UUID)

_LOGGER = logging.getLogger(__name__)

class SnoozDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, callback):
        bluepy.btle.DefaultDelegate.__init__(self)

        self.callback = callback

    def handleNotification(self, cHandle, data):
        on = data[1] == 0x01
        speed = data[0]
        self.callback(on=on, speed=speed)

class SnoozCommand():
    def __init__(self, on: bool = None, speed = None):
        self.on = on
        self.speed = speed

    def apply(self, device) -> None:

        if self.on is not None:
            device.set_on(self.on)
        
        if self.speed is not None:
            device.set_speed(self.speed)

class SnoozDevice():
    on = False
    speed = 1
    connected = False

    _sleep_task = None
    _stop = None
    _sleep_lock = None
    _command_lock = None
    _pending_command = None

    def __init__(self, on_state_change):
        self._stop = threading.Event()
        self._command_lock = RLock()
        self._sleep_lock = RLock()

        self._device = PeripheralWithConnectTimeout()

        def update_state(on=None, speed=None):
            was_changed = on is not self.on or speed is not self.speed

            self.on = on
            self.speed = speed

            if was_changed:
                on_state_change()

        self._device.setDelegate(SnoozDelegate(update_state))

    def stop(self):
        self._stop.set()

        if self.connected and self._device:
            try:
                self._device.disconnect()
            except:
                pass

        self._cancel_sleep()

    def start(self, address: str):
        thread = threading.Thread(target=self._run, args=[address])
        thread.daemon = True
        thread.start()

    def _run(self, address: str):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self._async_run(address))
        self.loop.close()

    async def _async_run(self, address: str):
        while True:
            if self._stop.isSet():
                return

            try:
                if self.connected:
                    self._execute_pending_command()
                    _LOGGER.info("[waiting for notifications]")
                    self._device.waitForNotifications(NOTIFICATION_TIMEOUT)
                else:
                    _LOGGER.info("[connecting]")
                    self._device.connect(address, timeout=CONNECTION_TIMEOUT)
                    _LOGGER.info("[connected]")
                    self._init_connection()
            except Exception as e:
                self._on_disconnected()

                if not isinstance(e, bluepy.btle.BTLEDisconnectError):
                    _LOGGER.exception("Unexpected exception in update thread")
            finally:
                self._execute_pending_command()
                await self._sleep()

    def set_on(self, on: bool):
        self._write_state(COMMAND_TURN_ON if on else COMMAND_TURN_OFF)

    def set_speed(self, speed: int):
        if speed < 0 or speed > 100:
            raise Exception("Invalid speed {}".format(speed))

        self._write_state([0x01, speed])

    def queue_command(self, command: SnoozCommand):
        with self._command_lock:
            self._pending_command = command

        self._cancel_sleep()

    def _execute_pending_command(self):
        if not self.connected:
            return

        with self._command_lock:
            if self._pending_command is not None and self.connected:
                self._pending_command.apply(self)
                self._pending_command = None
            

    def _init_connection(self):
        self.connected = True

        service = self._device.getServiceByUUID(SNOOZ_SERVICE_UUID)

        self._reader = service.getCharacteristics(READ_STATE_UUID)[0]
        self._writer = service.getCharacteristics(WRITE_STATE_UUID)[0]

        for bytes in CONNECTION_SEQUENCE:
            self._write_state(bytes)

        descriptor = self._reader.getDescriptors()[0]
        _LOGGER.info("[enable notifications]")
        descriptor.write(b"\x01\x00", withResponse=True)

    def _on_disconnected(self):
        self.connected = False
        self._reader = None
        self._writer = None

    async def _sleep(self):
        seconds = 1 if self.connected else CONNECTION_RETRY_INTERVAL

        with self._sleep_lock:
            self._sleep_task = self.loop.create_task(asyncio.sleep(seconds))
            try:
                await self._sleep_task
            except asyncio.CancelledError:
                pass
            self._sleep_task = None

    def _cancel_sleep(self):
        with self._sleep_lock:
            if self._sleep_task:
                self._sleep_task.cancel()
                self._sleep_task = None

    def _write_state(self, state: list):
        if self._writer == None:
            return
        try:
            _LOGGER.info("[writing] {}".format(' '.join(map(str, state))))
            self._writer.write(bytearray(state), withResponse=True)
        except:
            self._on_disconnected()
