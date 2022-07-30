"""Support for Snooz noise maker"""

import logging
from homeassistant.components.fan import DOMAIN, SUPPORT_SET_SPEED, FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TOKEN,
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .snooz import SnoozDevice

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    name: str = entry.data["name"]
    address: str = entry.data["address"]
    token: str = entry.data["token"]

    def on_state_change(on: bool, volume: int):
        def dispatch_update():
            hass.helpers.dispatcher.async_dispatcher_send(device_update_signal(address))

        hass.loop.call_soon_threadsafe(dispatch_update)

    device = SnoozDevice(address, token, on_state_change)

    @callback
    def async_start(_):
        hass.async_add_job(device.start)

    @callback
    def async_stop(_):
        device.stop()

    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, async_stop)

    if hass.is_running:
        async_start(None)
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_start)

    async_add_entities(
        [
            SnoozFan(
                hass,
                name,
                address,
                device,
            )
        ]
    )

    return True

class SnoozFan(FanEntity):
    def __init__(self, hass, name, address, device: SnoozDevice) -> None:
        self.hass = hass
        self._name = name
        self._address = address
        self._device = device

    @callback
    async def on_device_state_changed(self):
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.hass.helpers.dispatcher.async_dispatcher_connect(
                device_update_signal(self._address), self.on_device_state_changed
            )
        )

    async def async_will_remove_from_hass(self):
        self._device.stop()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._address)},
            "name": self.name,
            "manufacturer": "SNOOZ, INC.",
            "model": "SNOOZ White Noise Machine",
        }

    @property
    def unique_id(self):
        return self._address

    @property
    def name(self) -> str:
        return self._name

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
    def speed_count(self) -> int:
        return 100

    @property
    def percentage(self) -> int:
        return self._device.volume

    @property
    def is_on(self) -> bool:
        return self._device.on

    async def async_turn_on(self, speed=None, percentage=None, **kwargs) -> None:
        await self._device.handle_command(on=True, volume=speed)

    async def async_turn_off(self, **kwargs) -> None:
        await self._device.handle_command(on=False)

    async def async_set_percentage(self, percentage: int) -> None:
        await self._device.handle_command(volume=percentage)


def device_update_signal(id: str) -> str:
    return f"{DOMAIN}.update.{id}"