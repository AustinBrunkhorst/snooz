"""Support for SNOOZ noise maker"""

import logging
from collections.abc import Callable, Mapping
from datetime import timedelta
from typing import Any

import voluptuous as vol
from custom_components.snooz.const import DOMAIN
from custom_components.snooz.models import SnoozConfigurationData
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_ADDRESS, SERVICE_TURN_OFF,
                                 SERVICE_TURN_ON, STATE_OFF, STATE_ON)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.restore_state import RestoreEntity
from pysnooz.api import SnoozDeviceState, UnknownSnoozState
from pysnooz.commands import (SnoozCommandData, SnoozCommandResultStatus,
                              set_volume, turn_off, turn_on)
from pysnooz.device import SnoozConnectionStatus, SnoozDevice

# transitions logging is pretty verbose, so only enable warnings/errors
logging.getLogger("transitions.core").setLevel(logging.WARNING)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

ATTR_TRANSITION = "transition"
ATTR_VOLUME = "volume"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    """Set up SNOOZ device from a config entry."""
    
    address: str = entry.data[CONF_ADDRESS]
    data: SnoozConfigurationData = hass.data[DOMAIN][entry.entry_id]

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_TURN_ON,
        {
            vol.Optional(ATTR_VOLUME): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_TRANSITION): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=5*60)
            ),
        },
        "async_turn_on",
    )

    platform.async_register_entity_service(
        SERVICE_TURN_OFF,
        {
            vol.Optional(ATTR_TRANSITION): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=5*60)
            ),
        },
        "async_turn_off",
    )
    
    platform.async_register_entity_service(
        "disconnect",
        {},
        "async_disconnect",
    )
    
    async_add_entities(
        [
            SnoozFan(
                hass,
                data.device.display_name,
                address,
                data.device,
            )
        ]
    )

    return True


class SnoozFan(FanEntity, RestoreEntity):
    """Fan representation of SNOOZ device"""
    
    def __init__(self, hass, name: str, address: str, device: SnoozDevice) -> None:
        self.hass = hass
        self._address = address
        self._device = device
        self._attr_unique_id = address
        self._attr_supported_features = FanEntityFeature.SET_SPEED
        self._attr_name = name
        self._attr_is_on = None
        self._attr_should_poll = False
        self._attr_percentage = None
        self._last_command_successful = None

    def _write_state_changed(self) -> None:
        # cache state for restore entity
        if not self.assumed_state:
            self._attr_is_on = self._device.state.on
            self._attr_percentage = self._device.state.volume

        self.async_write_ha_state()

    def _on_connection_status_changed(self, new_status: SnoozConnectionStatus) -> None:
        self._write_state_changed()
        
    def _on_device_state_changed(self, new_state: SnoozDeviceState) -> None:
        self._write_state_changed()

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state == STATE_ON if last_state.state in (STATE_ON, STATE_OFF) else None
            self._attr_percentage = last_state.attributes.get("percentage")
            self._last_command_successful = last_state.attributes.get("last_command_successful")
            
        self.async_on_remove(self._subscribe_to_device_events())
    
    def _subscribe_to_device_events(self) -> Callable[[], None]:
        events = self._device.events
        
        def unsubscribe():
            events.on_connection_status_change -= self._on_connection_status_changed
            events.on_state_change -= self._on_device_state_changed
            
        events.on_connection_status_change += self._on_connection_status_changed
        events.on_state_change += self._on_device_state_changed
            
        return unsubscribe
        
    async def async_will_remove_from_hass(self):
        await self._device.async_disconnect()

    @property
    def percentage(self) -> int:
        return self._attr_percentage if self.assumed_state else self._device.state.volume

    @property
    def is_on(self) -> bool:
        return self._attr_is_on if self.assumed_state else self._device.state.on

    @property
    def assumed_state(self) -> bool:
        return not self._device.is_connected or self._device.state is UnknownSnoozState

    @property
    def extra_state_attributes(self) -> Mapping[Any, Any]:
        return {"last_command_successful": self._last_command_successful}

    async def async_disconnect(self, **kwargs) -> None:
        """Disconnect the underlying bluetooth device."""
        await self._device.async_disconnect()
        
    async def async_turn_on(self, percentage: int = None, preset_mode: str = None, **kwargs) -> None:
        transition = self._get_transition(kwargs)
        await self._async_execute_command(turn_on(percentage or kwargs.get("volume"), transition))

    async def async_turn_off(self, **kwargs) -> None:
        transition = self._get_transition(kwargs)
        await self._async_execute_command(turn_off(transition))

    async def async_set_percentage(self, percentage: int) -> None:
        await self._async_execute_command(set_volume(percentage))

    async def _async_execute_command(self, command: SnoozCommandData) -> None:
        result = await self._device.async_execute_command(command)
        self._last_command_successful = result.status == SnoozCommandResultStatus.SUCCESSFUL
        self.async_write_ha_state()

    def _get_transition(self, kwargs: Mapping[str, Any]) -> timedelta:
        seconds = kwargs.get(ATTR_TRANSITION)
        return timedelta(seconds=seconds) if seconds else None
