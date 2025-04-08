"""Secrets handler for SolarCloud integration."""

import os
import yaml
from homeassistant.const import CONF_SECRETS

SECRETS_FILE = "secrets.yaml"


def _get_secrets_path(hass):
    return os.path.join(hass.config.path(), SECRETS_FILE)


def _get_key(entry_id, key):
    """Genera clave única por entry."""
    return f"solarcloud_{entry_id}_{key}"


def load_secrets(hass, entry_id, keys):
    """Carga secretos desde secrets.yaml."""
    secrets_path = _get_secrets_path(hass)

    if not os.path.exists(secrets_path):
        return {}

    with open(secrets_path, "r", encoding="utf-8") as file:
        secrets = yaml.safe_load(file) or {}

    return {key: secrets.get(_get_key(entry_id, key), "") for key in keys}


def save_secrets(hass, entry_id, data):
    """Guarda secretos en secrets.yaml."""
    secrets_path = _get_secrets_path(hass)

    if os.path.exists(secrets_path):
        with open(secrets_path, "r", encoding="utf-8") as file:
            secrets = yaml.safe_load(file) or {}
    else:
        secrets = {}

    for key, value in data.items():
        if key in ["point_id_list"]:
            # Guarda las listas como string
            secrets[_get_key(entry_id, key)] = str(value)
        else:
            secrets[_get_key(entry_id, key)] = value

    with open(secrets_path, "w", encoding="utf-8") as file:
        yaml.dump(secrets, file, allow_unicode=True)
