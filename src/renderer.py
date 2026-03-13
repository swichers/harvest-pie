from term_piechart import Pie

def render_pie_chart(stats, config=None):
    worked = stats['worked']
    missing = stats['missing']
    
    if config is None:
        config = {}
        
    color_worked = config.get('color_worked', '#89cff0')
    color_missing = config.get('color_missing', '#ff7f7f')
    
    # Define data with custom hex colors
    data = [
        {"name": "Worked", "value": worked, "color": color_worked},
        {"name": "Missing", "value": missing, "color": color_missing},
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
