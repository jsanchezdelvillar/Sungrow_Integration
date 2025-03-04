import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .api import SolarAPI

_LOGGER = logging.getLogger(__name__)

def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration from configuration.yaml."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Crear instancia de la API y almacenarla en hass.data
    api = SolarAPI(hass, entry.data)
    hass.data[DOMAIN][entry.entry_id] = api
    
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an integration entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
