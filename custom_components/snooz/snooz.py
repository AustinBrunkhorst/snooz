import asyncio
import logging
import time
from bleak import BleakScanner,BleakClient

# uuid of the service that controls snooz
SNOOZ_SERVICE_UUID = "729f0608496a47fea1243a62aaa3fbc0"

# uuid of the characteristic that reads snooz state
READ_STATE_UUID = "80c37f00-cc16-11e4-8830-0800200c9a66"
READ_STATE_DESCRIPTOR_UUID = "00002902-0000-1000-8000-00805f9b34fb"

# uuid of the characteristic that writes snooz state
WRITE_STATE_UUID = "90759319-1668-44da-9ef3-492d593bd1e5"

# length in bytes of the read characteristic
STATE_UPDATE_LENGTH = 20

COMMAND_SET_TOKEN = "06"

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

logger = logging.getLogger(__name__)

logger.setLevel("DEBUG")

class SnoozDevice():

    def __init__(self, address: str, token: str, on_state_change):

        self.address = address
        self.token = token

        self.client = BleakClient(self.address, timeout=5)
        self.on_state_change = on_state_change
        self.on = False
        self.volume = 0
        
        token = COMMAND_SET_TOKEN + token

    # Hass.io appears to not always find Bluetooth LE devices with the default
    # scanning behavior. BleakScanner can set the OS level scanning filter,
    # so this is engaged each time communication with the Snooz is required
    # to ensure the OS can find it.
    async def turn_on_le_scan(self):
        async with BleakScanner() as scanner:
            scanner.set_scanning_filter(filters={"Transport": "le"})
            await scanner.start()
            return

    async def _write_state(self, state: list):
        await self.turn_on_le_scan()

        if not self.client.is_connected:
            await self.client.connect(timeout=20)
            await asyncio.sleep(1)

        await self.client.write_gatt_char(
            WRITE_STATE_UUID, 
            bytearray.fromhex(COMMAND_SET_TOKEN + self.token), 
            response=True
            )
    
        await self.client.write_gatt_char(
            WRITE_STATE_UUID, 
            bytearray(state), 
            response=True
            )

    async def handle_command(self, on: bool=None, volume: int=None):
        logger.info(f"Received command to handle: {on=} {volume=}")
        if on:
            await self._write_state(COMMAND_TURN_ON)
        elif volume:
            await self._write_state([0x01,volume])
        elif on == False:
            await self._write_state(COMMAND_TURN_OFF)
        
        await asyncio.sleep(1)
        
        state = await self.client.read_gatt_char(READ_STATE_UUID)
        
        on_state = state[1] == 1

        self.on = on_state
        self.volume = state[0]

        logger.info(f"Got state on={state[1]}, volume={state[0]}")
        self.on_state_change(on=on_state,volume=state[0])

    async def start(self):
        await self.turn_on_le_scan()
        await self.client.connect(timeout=20)

    async def stop(self):
        await self.turn_on_le_scan()
        await self.client.disconnect()
