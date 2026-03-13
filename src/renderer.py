from term_piechart import Pie

def render_pie_chart(stats):
    worked = stats['worked']
    missing = stats['missing']
    
    # Define data with custom hex colors
    # Bright pastel for worked, dark pastel for missing
    data = [
        {"name": "Worked", "value": worked, "color": "#89cff0"},
        {"name": "Missing", "value": missing, "color": "#4b5d67"},
    ]
    
    # Create pie chart
    try:
        # radius=10 is a good default for terminal
        pie = Pie(data, radius=10)
        print("\n" + str(pie))
    except Exception as e:
        print(f"Error rendering pie chart: {e}")

def render_summary(stats):
    print(f"\nWeekly Harvest Stats:")
    print(f"----------------------")
    print(f"Worked:    {stats['worked']:.2f} hrs")
    print(f"Scheduled: {stats['scheduled']:.2f} hrs")
    print(f"Missing:   {stats['missing']:.2f} hrs")
    print(f"----------------------")
