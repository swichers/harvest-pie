import requests
from datetime import datetime, timedelta
import sys

BASE_URL = "https://api.harvestapp.com/v2"
FORECAST_URL = "https://api.forecastapp.com"
DEFAULT_USER_AGENT = "Harvest Pie CLI (https://github.com/swichers/harvest-pie)"

def get_headers(config):
    return {
        "Authorization": f"Bearer {config['access_token']}",
        "Harvest-Account-Id": str(config['account_id']),
        "User-Agent": config.get("user_agent", DEFAULT_USER_AGENT)
    }

def get_forecast_headers(config):
    token = config.get('forecast_token') or config['access_token']
    return {
        "Authorization": f"Bearer {token}",
        "Forecast-Account-Id": str(config['forecast_account_id']),
        "User-Agent": config.get("user_agent", DEFAULT_USER_AGENT)
    }

def get_current_user(config):
    response = requests.get(f"{BASE_URL}/users/me", headers=get_headers(config))
    response.raise_for_status()
    return response.json()

def get_forecast_user(config):
    response = requests.get(f"{FORECAST_URL}/whoami", headers=get_forecast_headers(config))
    response.raise_for_status()
    return response.json()

def get_forecast_assignments(config, start_date, end_date, user_id):
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "user_id": user_id
    }
    response = requests.get(f"{FORECAST_URL}/assignments", headers=get_forecast_headers(config), params=params)
    response.raise_for_status()
    return response.json()

def get_time_entries(config, from_date, to_date, user_id):
    params = {
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "user_id": user_id
    }
    response = requests.get(f"{BASE_URL}/time_entries", headers=get_headers(config), params=params)
    response.raise_for_status()
    return response.json()

def get_work_days_count(start, end):
    """Count Monday-Friday days between start and end (inclusive)."""
    if start > end:
        return 0
    days_diff = (end - start).days + 1
    work_days = 0
    for d in range(days_diff):
        current_day = start + timedelta(days=d)
        if current_day.weekday() < 5:  # Mon-Fri
            work_days += 1
    return work_days

def calculate_stats(worked, scheduled, target):
    """
    Calculate worked, remaining, and under_target buckets.
    Worked: actually tracked.
    Remaining: Forecast - Worked.
    Under Target: Target - max(Forecast, Worked).
    """
    remaining = max(0.0, scheduled - worked)
    under_target = max(0.0, target - max(scheduled, worked))
    return {
        "worked": float(worked),
        "scheduled": float(scheduled),
        "target": float(target),
        "remaining": float(remaining),
        "under_target": float(under_target)
    }

def get_weekly_stats(config, force_worked=None, force_forecast=None):
    # Current week dates (Monday to Sunday)
    now = datetime.now()
    # Normalize today to start of day
    today = datetime(now.year, now.month, now.day)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    harvest_user_id = None
    if force_worked is None:
        harvest_user = get_current_user(config)
        harvest_user_id = harvest_user['id']

    # 1. Determine scheduled hours (Forecast/Manual/Capacity)
    if force_forecast is not None:
        scheduled_hours = force_forecast
    else:
        # Default fallback
        default_cap = config.get('default_capacity', 30.0)
        # We need the harvest user if forecast is missing
        if not harvest_user_id:
            harvest_user = get_current_user(config)
            harvest_user_id = harvest_user['id']

        scheduled_hours = harvest_user.get('weekly_capacity', default_cap * 3600) / 3600.0

        # Manual override in config
        if config.get('scheduled_hours'):
            scheduled_hours = float(config['scheduled_hours'])
        # Try Forecast if configured
        elif config.get('forecast_account_id'):
            try:
                forecast_me = get_forecast_user(config)
                forecast_user_id = forecast_me['current_user']['id']
                assignments = get_forecast_assignments(config, start_of_week, end_of_week, forecast_user_id)

                forecast_total = 0
                for assignment in assignments.get('assignments', []):
                    if assignment.get('person_id') != forecast_user_id:
                        continue

                    a_start = datetime.strptime(assignment['start_date'], "%Y-%m-%d")
                    a_end = datetime.strptime(assignment['end_date'], "%Y-%m-%d")

                    actual_start = max(start_of_week, a_start)
                    actual_end = min(end_of_week, a_end)

                    work_days = get_work_days_count(actual_start, actual_end)
                    forecast_total += (assignment.get('allocation', 0) * work_days / 3600.0)

                if forecast_total > 0:
                    scheduled_hours = forecast_total
            except Exception:
                pass

    # 2. Determine worked hours
    if force_worked is not None:
        worked = force_worked
    else:
        entries = get_time_entries(config, start_of_week, end_of_week, harvest_user_id)
        worked = sum(entry['hours'] for entry in entries.get('time_entries', []))

    # 3. Calculate target and final stats
    target = config.get('target_hours', 30.0)
    return calculate_stats(worked, scheduled_hours, target)
