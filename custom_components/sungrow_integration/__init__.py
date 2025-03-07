import logging
import os
import yaml
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_APPKEY, CONF_X_ACCESS_KEY, CONF_PUBLIC_KEY, CONF_PS_KEY, CONF_POINT_ID_LIST

_LOGGER = logging.getLogger(__name__)

def read_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'secrets.yaml')
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

secrets = read_secrets()

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the integration from configuration.yaml."""
    _LOGGER.debug("async_setup called with config: %s", config)
    hass.data.setdefault(DOMAIN, {})

    async def handle_get_sensor_data(call):
        """Handle the service call to get sensor data."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            sensors = entry_data.get("sensors", {})
            for sensor in sensors.values():
                await sensor.async_update_ha_state()

    async def handle_update_token(call):
        """Handle the service call to update the authentication token."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if "update_token" in entry_data:
                await entry_data["update_token"]()

    hass.services.async_register(DOMAIN, "get_sensor_data", handle_get_sensor_data)
    hass.services.async_register(DOMAIN, "update_token", handle_update_token)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""
    _LOGGER.debug("async_setup_entry called with entry: %s", entry.data)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_USERNAME: secrets.get(CONF_USERNAME, 'your_username'),
        CONF_PASSWORD: secrets.get(CONF_PASSWORD, 'your_password'),
        CONF_APPKEY: secrets.get(CONF_APPKEY, 'your_appkey'),
        CONF_X_ACCESS_KEY: secrets.get(CONF_X_ACCESS_KEY, 'your_x_access_key'),
        CONF_PUBLIC_KEY: secrets.get(CONF_PUBLIC_KEY, 'your_public_key'),
        CONF_PS_KEY: secrets.get(CONF_PS_KEY, 'your_ps_key'),
        CONF_POINT_ID_LIST: secrets.get(CONF_POINT_ID_LIST, ['your_point_id_1', 'your_point_id_2']),
        "sensor_names": secrets.get("sensor_names", {"sensor1": "Sensor 1", "sensor2": "Sensor 2"})
    }

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an integration entry."""
    _LOGGER.debug("async_unload_entry called for entry: %s", entry.entry_id)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
