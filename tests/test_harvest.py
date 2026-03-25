import pytest
from datetime import datetime
from src.harvest import get_work_days_count, calculate_stats, get_weekly_stats

def test_get_work_days_count():
    # Mon-Fri
    start = datetime(2026, 3, 9) # Monday
    end = datetime(2026, 3, 13) # Friday
    assert get_work_days_count(start, end) == 5

    # Full week Mon-Sun
    end_sun = datetime(2026, 3, 15) # Sunday
    assert get_work_days_count(start, end_sun) == 5

    # Mid week
    start_wed = datetime(2026, 3, 11) # Wednesday
    assert get_work_days_count(start_wed, end) == 3

    # Across weeks
    end_next_mon = datetime(2026, 3, 16) # Monday
    assert get_work_days_count(start, end_next_mon) == 6

def test_calculate_stats_under_target():
    # Target 40, Forecast 35, Worked 35
    stats = calculate_stats(worked=35, scheduled=35, target=40)
    assert stats['worked'] == 35.0
    assert stats['remaining'] == 0.0
    assert stats['gap'] == 5.0
    assert stats['under_target'] == 5.0

def test_calculate_stats_success():
    # Target 35, Forecast 35, Worked 35
    stats = calculate_stats(worked=35, scheduled=35, target=35)
    assert stats['worked'] == 35.0
    assert stats['remaining'] == 0.0
    assert stats['gap'] == 0.0
    assert stats['under_target'] == 0.0

def test_calculate_stats_remaining():
    # Target 35, Worked 30, Forecast 35
    stats = calculate_stats(worked=30, scheduled=35, target=35)
    assert stats['worked'] == 30.0
    assert stats['remaining'] == 5.0
    assert stats['gap'] == 0.0
    assert stats['under_target'] == 5.0

def test_get_weekly_stats_force(mocker):
    # Testing that force_worked and force_forecast bypass API
    config = {"target_hours": 30.0}
    
    # Mock API calls just in case they are triggered (they shouldn't be)
    mock_user = mocker.patch("src.harvest.get_current_user")
    mock_entries = mocker.patch("src.harvest.get_time_entries")
    
    stats = get_weekly_stats(config, force_worked=20.0, force_forecast=25.0)
    
    assert stats['worked'] == 20.0
    assert stats['scheduled'] == 25.0
    assert stats['remaining'] == 5.0
    assert stats['gap'] == 5.0 # 30 - 25
    assert stats['under_target'] == 10.0 # 30 - 20
    
    mock_user.assert_not_called()
    mock_entries.assert_not_called()

def test_get_weekly_stats_api_flow(mocker):
    config = {
        "access_token": "tk", 
        "account_id": "acc", 
        "target_hours": 40.0,
        "forecast_account_id": "f_acc"
    }
    
    # Mock Harvest User
    mocker.patch("src.harvest.get_current_user", return_value={"id": 1, "weekly_capacity": 35 * 3600})
    
    # Mock Forecast User
    mocker.patch("src.harvest.get_forecast_user", return_value={"current_user": {"id": 10}})
    
    # Mock Forecast Assignments (Return 35 hours total)
    # 5 days * 7 hours (25200 sec) = 35 hrs
    mocker.patch("src.harvest.get_forecast_assignments", return_value={
        "assignments": [
            {
                "person_id": 10,
                "start_date": "2026-03-09",
                "end_date": "2026-03-13",
                "allocation": 25200
            }
        ]
    })
    
    # Mock Harvest Time Entries (Return 30 hours)
    mocker.patch("src.harvest.get_time_entries", return_value={
        "time_entries": [{"hours": 10}, {"hours": 20}]
    })

    # Fix current date for test stability
    mock_now = datetime(2026, 3, 11) # Wednesday
    mocker.patch("src.harvest.datetime", mocker.Mock(wraps=datetime))
    import src.harvest
    src.harvest.datetime.now.return_value = mock_now

    stats = get_weekly_stats(config)
    
    assert stats['worked'] == 30.0
    assert stats['scheduled'] == 35.0 # From Forecast
    assert stats['target'] == 40.0
    assert stats['remaining'] == 5.0
    assert stats['gap'] == 5.0 # 40 - 35
    assert stats['under_target'] == 10.0 # 40 - 30

def test_calculate_stats_billable():
    # Target 40, billable target 80% (32 hrs)
    stats = calculate_stats(worked=35, scheduled=35, target=40, billable_worked=30, billable_target_ratio=0.8)
    assert stats['worked'] == 35.0
    assert stats['billable_worked'] == 30.0
    assert stats['billable_target'] == 32.0 # 40 * 0.8
    assert stats['target'] == 40.0

def test_get_weekly_stats_billable_mock(mocker):
    config = {
        "access_token": "tk", 
        "account_id": "acc", 
        "target_hours": 40.0,
        "billable_target_ratio": 0.5
    }
    
    # Mock Harvest User
    mocker.patch("src.harvest.get_current_user", return_value={"id": 1, "weekly_capacity": 40 * 3600})
    
    # Mock Harvest Time Entries (Return 30 hours total, 20 billable)
    mocker.patch("src.harvest.get_time_entries", return_value={
        "time_entries": [
            {"hours": 10, "billable": True}, 
            {"hours": 10, "billable": True},
            {"hours": 10, "billable": False}
        ]
    })

    # Fix current date
    mock_now = datetime(2026, 3, 11) # Wednesday
    mocker.patch("src.harvest.datetime", mocker.Mock(wraps=datetime))
    import src.harvest
    src.harvest.datetime.now.return_value = mock_now

    stats = get_weekly_stats(config)
    
    assert stats['worked'] == 30.0
    assert stats['billable_worked'] == 20.0
    assert stats['billable_target'] == 20.0 # 40 * 0.5
    assert stats['target'] == 40.0
