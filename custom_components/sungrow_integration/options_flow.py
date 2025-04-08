"""Options flow for SolarCloud integration."""

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN
from . import secrets_handler

CONF_API_KEY = "api_key"
CONF_SECRET_KEY = "secret_key"
CONF_RSA_KEY = "rsa_key"
CONF_PS_KEY = "ps_key"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POINT_ID_LIST = "point_id_list"


class SolarCloudOptionsFlow(config_entries.OptionsFlow):
    """Handle SolarCloud options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.secrets = secrets_handler.load_secrets(
            config_entry.hass, config_entry.entry_id
        )
        self.point_id_list = self.secrets.get(CONF_POINT_ID_LIST, [])

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.secrets.update(user_input)
            return await self.async_step_points()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY, default=self.secrets.get(CONF_API_KEY, "")): str,
                vol.Required(CONF_SECRET_KEY, default=self.secrets.get(CONF_SECRET_KEY, "")): str,
                vol.Required(CONF_RSA_KEY, default=self.secrets.get(CONF_RSA_KEY, "")): str,
                vol.Required(CONF_PS_KEY, default=self.secrets.get(CONF_PS_KEY, "")): str,
                vol.Required(CONF_USERNAME, default=self.secrets.get(CONF_USERNAME, "")): str,
                vol.Required(CONF_PASSWORD, default=self.secrets.get(CONF_PASSWORD, "")): str,
            }),
            errors=errors,
        )

    async def async_step_points(self, user_input=None):
        errors = {}

        if user_input is not None:
            if user_input.get("add_point"):
                return await self.async_step_add_point()

            if user_input.get("remove_point"):
                return await self.async_step_remove_point()

            secrets_handler.save_secrets(
                self.config_entry.hass, self.config_entry.entry_id, self.secrets
            )
            return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Optional("add_point"): bool,
            vol.Optional("remove_point"): bool,
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
            self.secrets[CONF_POINT_ID_LIST] = self.point_id_list
            return await self.async_step_points()

        return self.async_show_form(
            step_id="add_point",
            data_schema=vol.Schema({
                vol.Required("id"): str,
                vol.Required("name"): str,
            }),
            errors=errors,
        )

    async def async_step_remove_point(self, user_input=None):
        errors = {}

        choices = {str(i): f"{item[0]} - {item[1]}" for i, item in enumerate(self.point_id_list)}

        if user_input is not None:
            index = int(user_input["index"])
            self.point_id_list.pop(index)
            self.secrets[CONF_POINT_ID_LIST] = self.point_id_list
            return await self.async_step_points()

        return self.async_show_form(
            step_id="remove_point",
            data_schema=vol.Schema({
                vol.Required("index"): vol.In(choices),
            }),
            errors=errors,
        )
