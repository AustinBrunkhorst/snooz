from base64 import b64encode
import logging
from typing import List

from bleak import BleakScanner

from homeassistant.helpers.device_registry import format_mac

from .errors import BluetoothManagementNotAvailable

_LOGGER = logging.getLogger(__name__)

_LOGGER.setLevel("DEBUG")

class DiscoveredSnooz:
    def __init__(self, name: str, token: str, device):
        self.name: str = name
        self.token: str = token
        self.address: str = device.address
        self.id = format_mac(self.address)


class SnoozDiscoverer():
    devices = []

    def __init__(self):
        pass

    def handleDiscovery(self, devices):

        for device in devices:
            device_name = device.name
            if device_name and device_name.startswith("Snooz"):

                advertisement = device.metadata["manufacturer_data"][65535]

                token = advertisement.hex()[2:]

                snooz_device = DiscoveredSnooz(device_name, token, device)

                self.devices.append(snooz_device)


async def discover_snooz_devices() -> List[DiscoveredSnooz]:
    try:
        discoverer = SnoozDiscoverer()

        devices = await BleakScanner.discover()

        discoverer.handleDiscovery(devices)

        _LOGGER.info(f"Discoverer sending {len(discoverer.devices)} devices to onboarding")

        return discoverer.devices
    except BTLEManagementError as e:
        if "Management not available" in e.message:
            raise BluetoothManagementNotAvailable()
    except:
        _LOGGER.exception("Unable to discover SNOOZ devices")

        return []
