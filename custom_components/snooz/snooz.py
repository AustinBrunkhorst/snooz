import asyncio
from base64 import b64decode
import logging
import threading
from threading import Event, RLock

import bluepy.btle

from .peripheral import PeripheralWithTimeout

# uuid of the service that controls snooz
SNOOZ_SERVICE_UUID = "729f0608496a47fea1243a62aaa3fbc0"

# uuid of the characteristic that reads snooz state
READ_STATE_UUID = "80c37f00-cc16-11e4-8830-0800200c9a66"
READ_STATE_DESCRIPTOR_UUID = "00002902-0000-1000-8000-00805f9b34fb"

# uuid of the characteristic that writes snooz state
WRITE_STATE_UUID = "90759319-1668-44da-9ef3-492d593bd1e5"

# length in bytes of the read characteristic
STATE_UPDATE_LENGTH = 20

COMMAND_SET_TOKEN = b"\x06"

# bytes that turn on the snooz
COMMAND_TURN_ON = [0x02, 0x01]

# bytes that turn off the snooz
COMMAND_TURN_OFF = [0x02, 0x00]

# timeout for connections
CONNECTION_TIMEOUT = 10

# interval to retry connecting
CONNECTION_RETRY_INTERVAL = 3

# timeout for waiting on notifications
NOTIFICATION_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)


class SnoozStateReaderDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, callback):
        bluepy.btle.DefaultDelegate.__init__(self)

        self.callback = callback

    def handleNotification(self, cHandle, data):
        on = data[1] == 0x01
        volume = data[0]
        self.callback(on=on, volume=volume)


class SnoozCommand:
    def __init__(self, on: bool = None, volume=None):
        self.on = on
        self.volume = volume

    def apply(self, device) -> None:
        if self.on is not None:
            device.set_on(self.on)

        if self.volume is not None:
            device.set_volume(self.volume)


class SnoozDevice:
    on = False
    volume = 0
    connected: Event

    _sleep_task: asyncio.Task = None
    _stop: Event = None
    _sleep_lock: RLock = None
    _device_lock: RLock = None
    _command_lock: RLock = None
    _pending_command: SnoozCommand = None

    def __init__(self, address: str, token: str, on_state_change):
        self.connected = threading.Event()
        self._stop = threading.Event()
        self._command_lock = RLock()
        self._sleep_lock = RLock()

        self._address = address
        self._token = token
        self._device = PeripheralWithTimeout()

        def update_state(on=None, volume=None):
            was_changed = on != self.on or volume != self.volume

            self.on = on
            self.volume = volume

            if was_changed:
                on_state_change(on=on, volume=volume)

        self._device_update_handler = SnoozStateReaderDelegate(update_state)

    def stop(self):
        self._stop.set()
        self._cancel_sleep()

        if self.connected.is_set() and self._device:
            try:
                self._device.disconnect()
            except:
                pass
            finally:
                self.connected.clear()

    def start(self):
        self._stop.clear()

        update_thread = threading.Thread(
            target=self._run, name=f"SnoozDevice-{self._address}", daemon=True
        )
        update_thread.start()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self._async_update_loop())
        self.loop.close()

    async def _async_update_loop(self):
        _LOGGER.debug(f"[running] {self._address}")

        while not self._stop.is_set():
            try:
                if self.connected.is_set():
                    self._execute_pending_command()
                    self._device.waitForNotifications(NOTIFICATION_TIMEOUT)
                else:
                    _LOGGER.debug(f"[connecting] {self._address}")
                    self._device.connect(self._address, timeout=CONNECTION_TIMEOUT)
                    _LOGGER.debug(f"[connected] {self._address}")
                    self._init_connection()
            except Exception as e:
                self._on_disconnected()
                if not isinstance(e, bluepy.btle.BTLEDisconnectError):
                    _LOGGER.exception("Exception occurred")
            finally:
                self._execute_pending_command()
                await self._sleep()

    def set_on(self, on: bool):
        self._write_state(COMMAND_TURN_ON if on else COMMAND_TURN_OFF)

    def set_volume(self, volume: int):
        if volume < 0 or volume > 100:
            raise Exception(f"Invalid volume {volume}")

        self._write_state([0x01, volume])

    def queue_command(self, command: SnoozCommand):
        with self._command_lock:
            self._pending_command = command

        self._cancel_sleep()

    def _execute_pending_command(self):
        if not self.connected.is_set():
            return

        with self._command_lock:
            if self._pending_command is not None and self.connected.is_set():
                self._pending_command.apply(self)
                self._pending_command = None

    def _init_connection(self):
        self.connected.set()

        self._device.withDelegate(self._device_update_handler)

        service = self._device.getServiceByUUID(SNOOZ_SERVICE_UUID)

        self._reader = service.getCharacteristics(READ_STATE_UUID)[0]
        self._writer = service.getCharacteristics(WRITE_STATE_UUID)[0]

        stateDescriptor = self._reader.getDescriptors()[0]
        stateDescriptor.write(b"\x01\x00", True)

        _LOGGER.debug(f"[set token] {self._address} {self._token}")
        self._writer.write(
            COMMAND_SET_TOKEN + b64decode(self._token), withResponse=True
        )

    def _on_disconnected(self):
        _LOGGER.debug(f"[disconnected] {self._address}")
        self.connected.clear()
        self._reader = None
        self._writer = None

    async def _sleep(self):
        seconds = 0 if self.connected.is_set() else CONNECTION_RETRY_INTERVAL

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

    def _write_state(self, state: list):
        if self._writer == None:
            return
        try:
            self._writer.write(bytearray(state), withResponse=True)
        except:
            self._on_disconnected()
