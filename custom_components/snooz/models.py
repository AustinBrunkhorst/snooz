from bleak.backends.device import BLEDevice
from homeassistant.components.bluetooth.passive_update_processor import \
    PassiveBluetoothProcessorCoordinator
from pysnooz.device import SnoozDevice


class SnoozConfigurationData:
    """Configuration data for SNOOZ."""
    
    def __init__(self, ble_device: BLEDevice, device: SnoozDevice, coordinator: PassiveBluetoothProcessorCoordinator) -> None:
        self.ble_device = ble_device
        self.device = device
        self.coordinator = coordinator
