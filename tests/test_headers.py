from src.harvest import get_headers, get_forecast_headers, DEFAULT_USER_AGENT

def test_get_headers_default():
    config = {
        "access_token": "test_token",
        "account_id": "12345"
    }
    headers = get_headers(config)
    assert headers["User-Agent"] == DEFAULT_USER_AGENT
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Harvest-Account-Id"] == "12345"

def test_get_headers_custom():
    config = {
        "access_token": "test_token",
        "account_id": "12345",
        "user_agent": "Custom-Agent/1.0"
    }
    headers = get_headers(config)
    assert headers["User-Agent"] == "Custom-Agent/1.0"

def test_get_forecast_headers_default():
    config = {
        "access_token": "test_token",
        "forecast_account_id": "67890"
    }
    headers = get_forecast_headers(config)
    assert headers["User-Agent"] == DEFAULT_USER_AGENT
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Forecast-Account-Id"] == "67890"

def test_get_forecast_headers_custom_token():
    config = {
        "access_token": "test_token",
        "forecast_token": "forecast_token",
        "forecast_account_id": "67890",
        "user_agent": "Custom-Agent/2.0"
    }
    headers = get_forecast_headers(config)
    assert headers["User-Agent"] == "Custom-Agent/2.0"
    assert headers["Authorization"] == "Bearer forecast_token"
