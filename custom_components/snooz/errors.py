"""Errors for the SNOOZ component."""
from homeassistant.exceptions import HomeAssistantError


class SnoozException(HomeAssistantError):
    """Base class for SNOOZ exceptions."""


class BluetoothManagementNotAvailable(SnoozException):
    """Bluetooth management not available on host"""
