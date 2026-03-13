from src.harvest import get_weekly_stats
from src.renderer import render_pie_chart, render_summary

def test_display():
    # Mock stats
    stats = {
        "worked": 28.5,
        "scheduled": 35.0,
        "missing": 6.5
    }
    print("Testing summary display:")
    render_summary(stats)
    print("\nTesting pie chart display:")
    render_pie_chart(stats)

if __name__ == "__main__":
    test_display()
