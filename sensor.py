import logging
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SolarSensor(coordinator, "Power Output")])

class SolarSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, coordinator: DataUpdateCoordinator, name: str):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = name
        self._state = None
    
    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch new state data."""
        await self._coordinator.async_request_refresh()
        self._state = self._coordinator.data.get("power_output")
