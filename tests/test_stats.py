from src.renderer import render_pie_chart, render_summary

def test_display():
    # Mock stats matching new structure
    stats = {
        "worked": 28.5,
        "scheduled": 35.0,
        "target": 30.0,
        "remaining": 6.5,
        "under_target": 0.0
    }
    print("Testing summary display:")
    render_summary(stats)
    print("\nTesting pie chart display:")
    # We pass a mock config for colors
    render_pie_chart(stats, {"color_worked": "#56B4E9"})

if __name__ == "__main__":
    test_display()
