from src.renderer import render_pie_chart, render_summary

def test_display():
    # Mock stats matching new structure
    # Target 35, Forecast 30, Worked 20
    # Billable Target = 35 * 0.5 = 17.5
    # Billable Worked = 8.75 (50% progress)
    stats = {
        "worked": 20.0,
        "billable_worked": 8.75,
        "billable_target": 17.5,
        "scheduled": 30.0,
        "target": 35.0,
        "remaining": 10.0,
        "under_target": 15.0,
        "gap": 5.0
    }
    print("Testing summary display:")
    render_summary(stats)
    
    print("\nTesting pie chart display (50% billable):")
    # We pass a mock config for colors
    render_pie_chart(stats, {"color_worked": "#56B4E9"})

    # 100% progress
    stats_100 = stats.copy()
    stats_100["billable_worked"] = 17.5
    print("\nTesting pie chart display (100% billable):")
    render_pie_chart(stats_100, {"color_worked": "#56B4E9"})

if __name__ == "__main__":
    test_display()
