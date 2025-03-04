import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_APPKEY, CONF_X_ACCESS_KEY, CONF_PUBLIC_KEY, CONF_PS_KEY, CONF_POINT_ID_LIST
import homeassistant.helpers.secrets as secrets

_LOGGER = logging.getLogger(__name__)

class CustomSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Custom Solar integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(title="Custom Solar", data=user_input)
        
        existing_secrets = await self.hass.async_add_executor_job(secrets.load_yaml, self.hass.config.path("secrets.yaml"))
        
        default_values = {
            CONF_USERNAME: existing_secrets.get(CONF_USERNAME, ""),
            CONF_PASSWORD: existing_secrets.get(CONF_PASSWORD, ""),
            CONF_APPKEY: existing_secrets.get(CONF_APPKEY, ""),
            CONF_X_ACCESS_KEY: existing_secrets.get(CONF_X_ACCESS_KEY, ""),
            CONF_PUBLIC_KEY: existing_secrets.get(CONF_PUBLIC_KEY, ""),
            CONF_PS_KEY: existing_secrets.get(CONF_PS_KEY, ""),
            CONF_POINT_ID_LIST: ",".join(existing_secrets.get(CONF_POINT_ID_LIST, [])),
        }

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=default_values[CONF_USERNAME]): cv.string,
                vol.Required(CONF_PASSWORD, default=default_values[CONF_PASSWORD]): cv.string,
                vol.Required(CONF_APPKEY, default=default_values[CONF_APPKEY]): cv.string,
                vol.Required(CONF_X_ACCESS_KEY, default=default_values[CONF_X_ACCESS_KEY]): cv.string,
                vol.Required(CONF_PUBLIC_KEY, default=default_values[CONF_PUBLIC_KEY]): cv.string,
                vol.Required(CONF_PS_KEY, default=default_values[CONF_PS_KEY]): cv.string,
                vol.Required(CONF_POINT_ID_LIST, default=default_values[CONF_POINT_ID_LIST]): cv.string,
            }
        )
        
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
