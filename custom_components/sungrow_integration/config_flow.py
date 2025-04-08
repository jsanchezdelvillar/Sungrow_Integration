"""Config flow for SolarCloud integration."""

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import uuid

from .const import DOMAIN
from . import secrets_handler


CONF_API_KEY = "api_key"
CONF_SECRET_KEY = "secret_key"
CONF_RSA_KEY = "rsa_key"
CONF_PS_KEY = "ps_key"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POINT_ID_LIST = "point_id_list"


class SolarCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolarCloud."""

    VERSION = 1

    def __init__(self):
        self.data = {}
        self.point_id_list = []

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_points()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_SECRET_KEY): str,
                vol.Required(CONF_RSA_KEY): str,
                vol.Required(CONF_PS_KEY): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_points(self, user_input=None):
        errors = {}

        if user_input is not None:
            if user_input.get("add_point"):
                return await self.async_step_add_point()

            self.data[CONF_POINT_ID_LIST] = self.point_id_list
            return self.async_create_entry(title="SolarCloud", data={})

        schema = vol.Schema({
            vol.Optional("add_point"): bool,
        })

        return self.async_show_form(
            step_id="points",
            data_schema=schema,
            description_placeholders={
                "points": str(self.point_id_list)
            },
            errors=errors,
        )

    async def async_step_add_point(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.point_id_list.append((user_input["id"], user_input["name"]))
            return await self.async_step_points()

        return self.async_show_form(
            step_id="add_point",
            data_schema=vol.Schema({
                vol.Required("id"): str,
                vol.Required("name"): str,
            }),
            errors=errors,
        )

    async def async_create_entry(self, title, data):
        entry = await super().async_create_entry(title=title, data=data)

        # Guardar en secrets.yaml
        keys = [
            CONF_API_KEY,
            CONF_SECRET_KEY,
            CONF_RSA_KEY,
            CONF_PS_KEY,
            CONF_USERNAME,
            CONF_PASSWORD,
            CONF_POINT_ID_LIST,
        ]
        save_data = self.data.copy()
        save_data[CONF_POINT_ID_LIST] = self.point_id_list

        secrets_handler.save_secrets(self.hass, entry.entry_id, save_data)

        return entry

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import SolarCloudOptionsFlow
        return SolarCloudOptionsFlow(config_entry)
