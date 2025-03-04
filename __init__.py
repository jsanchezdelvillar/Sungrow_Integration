import logging
import asyncio
import aiohttp
import voluptuous as vol
import json
import random
import string
import time
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity

DOMAIN = "custom_solar"
_LOGGER = logging.getLogger(__name__)

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_APPKEY = "appkey"
CONF_X_ACCESS_KEY = "sung_secret"
CONF_PUBLIC_KEY = "RSA_public"
CONF_PS_KEY = "ps_key"
CONF_POINT_ID_LIST = "point_id_list"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_APPKEY): cv.string,
                vol.Required(CONF_X_ACCESS_KEY): cv.string,
                vol.Required(CONF_PUBLIC_KEY): cv.string,
                vol.Required(CONF_PS_KEY): cv.string,
                vol.Required(CONF_POINT_ID_LIST): vol.All(cv.ensure_list, [cv.string]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration from configuration.yaml."""
    hass.data[DOMAIN] = {}
    if DOMAIN in config:
        hass.data[DOMAIN]["config"] = config[DOMAIN]
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from the UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an integration entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

async def get_token(session, username, password, appkey, x_access_key, public_key_base64):
    """Obtain a new token from the API."""
    login_url = "https://gateway.isolarcloud.eu/openapi/login"
    unenc_x_random_secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    x_random_secret_key = public_encrypt(unenc_x_random_secret_key, public_key_base64)
    nonce = generate_nonce()
    timestamp = str(int(time.time() * 1000))

    login_payload = {
        "api_key_param": {"nonce": nonce, "timestamp": timestamp},
        "appkey": appkey,
        "login_type": "1",
        "user_account": username,
        "user_password": password
    }
    login_headers = {
        "User-Agent": "Home Assistant",
        "x-access-key": x_access_key,
        "x-random-secret-key": x_random_secret_key,
        "Content-Type": "application/json",
        "sys_code": "901"
    }
    encrypted_request_body = encrypt(json.dumps(login_payload), unenc_x_random_secret_key)

    async with session.post(login_url, headers=login_headers, data=encrypted_request_body) as response:
        if response.status == 200:
            response_body = await response.text()
            decrypted_response_body = decrypt(response_body, unenc_x_random_secret_key)
            response_json = json.loads(decrypted_response_body)
            if response_json.get("result_code") == "1" and response_json.get("result_data", {}).get("login_state") == "1":
                return response_json["result_data"].get("token", "")
        return None

async def get_device_data(session, token, appkey, x_access_key, public_key_base64, ps_key, point_id_list):
    """Obtain device data using the current token."""
    device_data_url = "https://gateway.isolarcloud.eu/openapi/getDeviceRealTimeData"
    unenc_x_random_secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    x_random_secret_key = public_encrypt(unenc_x_random_secret_key, public_key_base64)
    nonce = generate_nonce()
    timestamp = str(int(time.time() * 1000))

    headers = {
        "User-Agent": "Home Assistant",
        "x-access-key": x_access_key,
        "x-random-secret-key": x_random_secret_key,
        "Content-Type": "application/json",
        "token": token,
        "sys_code": "901"
    }
    device_data_payload = {
        "api_key_param": {"nonce": nonce, "timestamp": timestamp},
        "appkey": appkey,
        "device_type": 11,
        "point_id_list": point_id_list,
        "ps_key_list": [ps_key]
    }
    encrypted_request_body = encrypt(json.dumps(device_data_payload), unenc_x_random_secret_key)

    async with session.post(device_data_url, headers=headers, data=encrypted_request_body) as response:
        if response.status == 200:
            response_body = await response.text()
            decrypted_response_body = decrypt(response_body, unenc_x_random_secret_key)
            return json.loads(decrypted_response_body)
        return None
