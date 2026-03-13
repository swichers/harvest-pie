import pytest
import json
import os
from click.testing import CliRunner
from src.cli import cli
from src import config

def test_cli_config(mocker, tmp_path):
    c_path = tmp_path / "config_test.json"
    mocker.patch("src.config.CONFIG_PATH", c_path)
    
    runner = CliRunner()
    # Provide all required options to avoid prompts
    result = runner.invoke(cli, [
        "config", 
        "--token", "tok", 
        "--account", "acc", 
        "--forecast-account", "f_acc", 
        "--target-hours", "35"
    ])
    
    assert result.exit_code == 0, result.output
    assert "Configuration saved" in result.output
    
    with open(c_path, "r") as f:
        data = json.load(f)
    assert data["access_token"] == "tok"
    assert data["account_id"] == "acc"
    assert data["forecast_account_id"] == "f_acc"
    assert data["target_hours"] == 35.0

def test_cli_main_run(mocker):
    mocker.patch("src.cli.is_configured", return_value=True)
    mocker.patch("src.cli.get_config", return_value={"target_hours": 30.0})
    
    mock_stats = mocker.patch("src.cli.get_weekly_stats", return_value={
        "worked": 10, "scheduled": 20, "target": 30, "remaining": 10, "under_target": 10
    })
    
    mocker.patch("src.cli.render_summary")
    mocker.patch("src.cli.render_pie_chart")
    
    runner = CliRunner()
    result = runner.invoke(cli, ["--force-worked", "15", "--force-forecast", "25"])
    
    assert result.exit_code == 0, result.output
    mock_stats.assert_called_once_with(mocker.ANY, force_worked=15.0, force_forecast=25.0)
