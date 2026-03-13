import requests
from datetime import datetime, timedelta
import sys

BASE_URL = "https://api.harvestapp.com/v2"
FORECAST_URL = "https://api.forecastapp.com"

def get_headers(config):
    return {
        "Authorization": f"Bearer {config['access_token']}",
        "Harvest-Account-Id": str(config['account_id']),
        "User-Agent": "Harvest Pie CLI (https://github.com/yourusername/harvest-pie)"
    }

def get_forecast_headers(config):
    token = config.get('forecast_token') or config['access_token']
    return {
        "Authorization": f"Bearer {token}",
        "Forecast-Account-Id": str(config['forecast_account_id']),
        "User-Agent": "Harvest Pie CLI (https://github.com/yourusername/harvest-pie)"
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

def get_weekly_stats(config):
    # Current week dates (Monday to Sunday)
    now = datetime.now()
    # Normalize today to start of day
    today = datetime(now.year, now.month, now.day)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    harvest_user = get_current_user(config)
    harvest_user_id = harvest_user['id']

    # 1. Start with Harvest capacity (fallback)
    default_cap = config.get('default_capacity', 30.0)
    scheduled_hours = harvest_user.get('weekly_capacity', default_cap * 3600) / 3600.0
    # 2. Manual override always wins if present
    if config.get('scheduled_hours'):
        scheduled_hours = float(config['scheduled_hours'])
    # 3. Try to get from Forecast if configured
    elif config.get('forecast_account_id'):
        try:
            forecast_me = get_forecast_user(config)
            forecast_user_id = forecast_me['current_user']['id']
            assignments = get_forecast_assignments(config, start_of_week, end_of_week, forecast_user_id)

            forecast_total = 0
            for assignment in assignments.get('assignments', []):
                # Filter by user manually because the API might return more
                if assignment.get('person_id') != forecast_user_id:
                    continue

                # Parse assignment dates
                a_start = datetime.strptime(assignment['start_date'], "%Y-%m-%d")
                a_end = datetime.strptime(assignment['end_date'], "%Y-%m-%d")

                # Intersection of assignment and current week
                actual_start = max(start_of_week, a_start)
                actual_end = min(end_of_week, a_end)

                if actual_start > actual_end:
                    continue

                # Calculate number of work days (Mon-Fri) in the overlap
                days_diff = (actual_end - actual_start).days + 1
                work_days = 0
                for d in range(days_diff):
                    current_day = actual_start + timedelta(days=d)
                    if current_day.weekday() < 5: # 0-4 is Mon-Fri
                        work_days += 1

                # Allocation is in seconds per day
                forecast_total += (assignment.get('allocation', 0) * work_days / 3600.0)

            if forecast_total > 0:
                scheduled_hours = forecast_total
        except Exception as e:
            # Fallback silently or log? Let's just fall back to Harvest capacity for now.
            pass

    entries = get_time_entries(config, start_of_week, end_of_week, harvest_user_id)
    total_hours = sum(entry['hours'] for entry in entries.get('time_entries', []))

    return {
        "worked": total_hours,
        "scheduled": scheduled_hours,
        "missing": max(0, scheduled_hours - total_hours)
    }
