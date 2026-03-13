import requests
from datetime import datetime, timedelta
import sys

BASE_URL = "https://api.harvestapp.com/v2"

def get_headers(config):
    return {
        "Authorization": f"Bearer {config['access_token']}",
        "Harvest-Account-Id": str(config['account_id']),
        "User-Agent": "Harvest Pie CLI (https://github.com/yourusername/harvest-pie)"
    }

def get_current_user(config):
    response = requests.get(f"{BASE_URL}/users/me", headers=get_headers(config))
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
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    user = get_current_user(config)
    user_id = user['id']
    
    # Harvest returns weekly_capacity in seconds
    weekly_capacity = user.get('weekly_capacity', 35 * 3600) / 3600.0
    
    # If user has a custom override in config
    if config.get('scheduled_hours'):
        weekly_capacity = float(config['scheduled_hours'])

    entries = get_time_entries(config, start_of_week, end_of_week, user_id)
    total_hours = sum(entry['hours'] for entry in entries.get('time_entries', []))

    return {
        "worked": total_hours,
        "scheduled": weekly_capacity,
        "missing": max(0, weekly_capacity - total_hours)
    }
