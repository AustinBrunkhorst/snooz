"""Support for Snooz noise maker"""
import logging
import asyncio
from bluepy import btle
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.const import (CONF_NAME, STATE_ON, STATE_OFF, STATE_UNKNOWN, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
from homeassistant.components.fan import (PLATFORM_SCHEMA, FanEntity, DOMAIN, SUPPORT_SET_SPEED)
from datetime import datetime
from .const import (
    DOMAIN,
    CONF_ADDRESS,
)
from .snooz_device import SnoozeDevice

_LOGGER = logging.getLogger(__name__)

SIGNAL_STATE_UPDATED = f"{DOMAIN}.updated"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_ADDRESS): cv.string
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    def on_state_change():
        hass.helpers.dispatcher.async_dispatcher_send(SIGNAL_STATE_UPDATED)

    device = SnoozeDevice(hass.loop, on_state_change)
    address = config[CONF_ADDRESS]
    name = config.get(CONF_NAME)

    @callback
    def async_start(_):
        hass.async_add_job(device.start, address)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_start)

    @callback
    def async_stop(_):
        device.stop()

    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, async_stop)
    
    async_add_entities([SnoozFan(hass, name, address, device)])

    return True

class SnoozFan(FanEntity):
    def __init__(self, hass, name, address, device) -> None:
        self.hass = hass
        self._name = name
        self._address = address
        self._id = self._address.split(":")[-2:]
        self._device = device

    @callback
    async def on_updated(self):
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.hass.helpers.dispatcher.async_dispatcher_connect(
                SIGNAL_STATE_UPDATED, 
                self.on_updated
            )
        )

    @property 
    def default_name(self) -> str:
        return "Snooz {}".format("".join(self._id))

    @property
    def name(self) -> str:
        return self._name if self._name else self.default_name

    @property
    def supported_features(self):
        return SUPPORT_SET_SPEED

    @property
    def available(self) -> bool:
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def percentage(self) -> int:
        return self._device.level * 10

    @property
    def is_on(self) -> bool:
        return self._device.on

    def turn_on(self, speed = None, percentage = None, **kwargs) -> None:
        def write_state():
            self._device.set_on(True)
            if percentage != None:
                self._set_device_percentage(percentage)
        
        self._device.queue_state(write_state)

    def turn_off(self, **kwargs) -> None:
        def write_state():
            self._device.set_on(False)
        
        self._device.queue_state(write_state)

    def set_percentage(self, percentage: str) -> None:
        def write_state():
            self._set_device_percentage(percentage)

        self._device.queue_state(write_state)

    def _set_device_percentage(self, percentage: int):
        self._device.set_level(int(percentage / 10))
