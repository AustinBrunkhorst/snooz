"""Config flow for SNOOZ Noise Maker."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS, CONF_NAME, CONF_TOKEN

from .const import DOMAIN
from .discovery import DiscoveredSnooz, discover_snooz_devices
from .errors import BluetoothManagementNotAvailable


class SnoozConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SNOOZ config flow."""

    VERSION = 1

    _title = "SNOOZ Noise Maker"

    def __init__(self) -> None:
        self.discovered_devices: dict[str, DiscoveredSnooz] | None = None

    async def async_step_user(self, user_input: dict | None = None) -> dict:
        """Handle a flow initialized by the user."""

        if (
            user_input is not None
            and self.discovered_devices is not None
            and user_input["id"] in self.discovered_devices
        ):
            device = self.discovered_devices[user_input["id"]]

            await self.async_set_unique_id(device.id, raise_on_progress=False)

            return self.create_device_entry(device)

        try:
            devices = discover_snooz_devices()
        except BluetoothManagementNotAvailable:
            return self.async_abort(reason="btle_not_available")

        if devices:
            already_configured = self._async_current_ids(False)
            devices = [
                device for device in devices if device.id not in already_configured
            ]
            self.discovered_devices = {device.id: device for device in devices}

        # no devices found
        if not self.discovered_devices:
            return self.async_abort(reason="no_devices_found")

        # 1 device found - confirm selection
        if len(self.discovered_devices) == 1:
            return await self.async_step_confirm_default_device()

        # allow the user to choose from multiple discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "id", default=self.default_discovered_device.id
                    ): vol.In({**{device.id: device.name for device in devices}})
                }
            ),
        )

    async def async_step_confirm_default_device(self, user_input=None):
        """Confirm default device selection."""
        default_device = self.default_discovered_device

        if user_input is not None:
            return self.create_device_entry(default_device)

        self._set_confirm_only()

        return self.async_show_form(
            step_id="confirm_default_device",
            description_placeholders={
                "name": default_device.name,
                "address": default_device.address,
            },
        )

    def create_device_entry(self, device: DiscoveredSnooz) -> dict:
        return self.async_create_entry(
            title=device.name,
            data={
                CONF_NAME: device.name,
                CONF_ADDRESS: device.address,
                CONF_TOKEN: device.token,
            },
        )

    @property
    def default_discovered_device(self) -> DiscoveredSnooz:
        return list(self.discovered_devices.values())[0]
