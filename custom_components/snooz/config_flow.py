"""Config flow for SNOOZ Noise Maker."""
from .discovery import discover

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN


async def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    devices = await hass.async_add_executor_job(discover)
    return len(devices) > 0


config_entry_flow.register_discovery_flow(
    DOMAIN,
    "SNOOZ Noise Maker",
    _async_has_devices,
    config_entries.CONN_CLASS_LOCAL_POLL,
)
