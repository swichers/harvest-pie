import pytest
import json
from src import config
from pathlib import Path

def test_get_config_missing(mocker, tmp_path):
    c_path = tmp_path / "non_existent.json"
    mocker.patch("src.config.CONFIG_PATH", c_path)
    assert config.get_config() == {}

def test_get_config_invalid_json(mocker, tmp_path):
    c_path = tmp_path / "config.json"
    mocker.patch("src.config.CONFIG_PATH", c_path)
    c_path.write_text("invalid json")
    assert config.get_config() == {}

def test_update_config(mocker, tmp_path):
    c_path = tmp_path / "config.json"
    mocker.patch("src.config.CONFIG_PATH", c_path)
    
    config.update_config("key", "value")
    
    with open(c_path, "r") as f:
        data = json.load(f)
    assert data["key"] == "value"

def test_is_configured(mocker):
    mocker.patch("src.config.get_config", return_value={"access_token": "tk", "account_id": "acc"})
    assert config.is_configured() is True
    
    mocker.patch("src.config.get_config", return_value={"access_token": "tk"})
    assert config.is_configured() is False
