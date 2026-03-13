import json
import os
from pathlib import Path

CONFIG_PATH = Path("config.json")

def get_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def update_config(key, value):
    config = get_config()
    config[key] = value
    save_config(config)

def is_configured():
    config = get_config()
    return "access_token" in config and "account_id" in config
