import logging
import asyncio
from bluepy import btle
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.const import (STATE_ON, STATE_OFF, STATE_UNKNOWN, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
from homeassistant.components.fan import (PLATFORM_SCHEMA, FanEntity, DOMAIN, SPEED_OFF, SUPPORT_SET_SPEED)
from datetime import datetime
from .const import (
    DOMAIN,
    CONF_ADDRESS,
)
from .snooz_device import SnoozeDevice

_LOGGER = logging.getLogger(__name__)

_VALID_SPEEDS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
SIGNAL_STATE_UPDATED = f"{DOMAIN}.updated"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ADDRESS): cv.string
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    def on_state_change():
        hass.helpers.dispatcher.async_dispatcher_send(SIGNAL_STATE_UPDATED)

    device = SnoozeDevice(hass.loop, on_state_change)
    address = config[CONF_ADDRESS]

    @callback
    def async_start(_):
        hass.async_add_job(device.start, address)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_start)

    @callback
    def async_stop(_):
        device.stop()

    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, async_stop)
        
    async_add_entities([SnoozFan(hass, address, device)])

    return True

class SnoozFan(FanEntity):
    def __init__(self, hass, address, device) -> None:
        self.hass = hass
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
    def name(self) -> str:
        return "Snooz {}".format("".join(self._id))

    @property
    def available(self) -> bool:
        return self._device.connected

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def speed(self) -> str:
        return "{:d}".format(self._device.level)

    @property
    def speed_list(self) -> list:
        return _VALID_SPEEDS

    @property
    def is_on(self) -> bool:
        return self._device.on

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED

    def turn_on(self, speed: str = None, **kwargs) -> None:
        self._device.set_on(True)

        if speed != None:
            self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        self._device.set_on(False)

    def set_speed(self, speed: str) -> None:
        if speed in _VALID_SPEEDS or speed == STATE_UNKNOWN:
            self._device.set_level(int(speed))
        else:
            _LOGGER.error("Received invalid speed: {}".format(speed))
