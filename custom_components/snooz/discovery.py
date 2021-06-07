from base64 import b64encode
import logging
from typing import List

from bluepy.btle import BTLEManagementError, DefaultDelegate, ScanEntry, Scanner

from homeassistant.helpers.device_registry import format_mac

from .errors import BluetoothManagementNotAvailable

_LOGGER = logging.getLogger(__name__)


class DiscoveredSnooz:
    def __init__(self, name: str, token: str, device: ScanEntry):
        self.name: str = name
        self.token: str = token
        self.address: str = device.addr
        self.id = format_mac(self.address)


class SnoozDiscoverer(DefaultDelegate):
    devices = []

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device: ScanEntry, isNew: bool, isData: bool):
        if not isNew:
            return

        device_name = device.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)

        if not isinstance(device_name, str) or not device_name.startswith("Snooz"):
            return

        advertisement = device.getValue(ScanEntry.MANUFACTURER)

        # unexpected data
        if len(advertisement) < 3:
            return

        if advertisement[:3] == b"\xFF\xFF\x08":
            _LOGGER.warning(
                f"Discovered {device_name} ({device.addr}) but it is not in pairing mode."
            )
            return

        token = b64encode(advertisement[3:]).decode("UTF-8")

        snooz_device = DiscoveredSnooz(device_name, token, device)

        self.devices.append(snooz_device)


def discover_snooz_devices() -> List[DiscoveredSnooz]:
    try:
        discoverer = SnoozDiscoverer()

        scanner = Scanner().withDelegate(discoverer)
        scanner.scan(5.0)

        return discoverer.devices
    except BTLEManagementError as e:
        if "Management not available" in e.message:
            raise BluetoothManagementNotAvailable()
    except:
        _LOGGER.exception("Unable to discover SNOOZ devices")

        return []
