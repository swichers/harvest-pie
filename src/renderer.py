from term_piechart import Pie

def render_pie_chart(stats, config=None):
    worked = stats['worked']
    remaining = stats['remaining']
    gap = stats.get('gap', 0.0)
    
    if config is None:
        config = {}
        
    # High-contrast, colorblind-friendly palette (Wong palette)
    color_worked = config.get('color_worked', '#56B4E9')       # Sky Blue
    color_remaining = config.get('color_remaining', '#CC79A7') # Reddish Purple
    color_under_target = config.get('color_under_target', '#E69F00') # Orange
    
    # Define data with custom hex colors
    data = []
    if worked > 0:
        data.append({"name": "Worked", "value": worked, "color": color_worked})
    if remaining > 0:
        data.append({"name": "Remaining", "value": remaining, "color": color_remaining})
    if gap > 0:
        data.append({"name": "Gap", "value": gap, "color": color_under_target})
    
    # Create pie chart
    try:
        if not data:
            print("No hours to display.")
            return
            
        pie = Pie(data, radius=10)
        print("\n" + str(pie))
    except Exception as e:
        print(f"Error rendering pie chart: {e}")

def render_summary(stats):
    green = "\033[92m"
    reset = "\033[0m"
    
    worked = stats['worked']
    billable_worked = stats.get('billable_worked', 0.0)
    billable_target = stats.get('billable_target', 0.0)
    forecast = stats['scheduled']
    target = stats['target']
    under_target = stats['under_target']
    remaining = stats['remaining']
    
    target_style = green if worked >= target else ""
    forecast_style = green if worked >= forecast else ""
    billable_style = green if billable_worked >= billable_target and billable_target > 0 else ""
    
    print(f"\nWeekly Status:")
    print(f"----------------------")
    print(f"Worked:       {worked:.2f} hrs")
    if billable_target > 0:
        print(f"{billable_style}Billable:     {billable_worked:.2f} / {billable_target:.2f} hrs{reset if billable_style else ''}")
    else:
        print(f"Billable:     {billable_worked:.2f} hrs")
    print(f"{forecast_style}Forecast:     {forecast:.2f} hrs{reset if forecast_style else ''}")
    print(f"{target_style}Target:       {target:.2f} hrs{reset if target_style else ''}")
    print(f"----------------------")
    
    if remaining > 0:
        print(f"Remaining to work: {remaining:.2f} hrs")
    
    if under_target > 0:
        print(f"FLAG: Under target by {under_target:.2f} hrs")
        if stats.get('gap', 0) > 0:
             print(f"      ({stats['gap']:.2f} hrs unscheduled)")
    elif worked >= target:
        print("Success: Target achieved!")
    elif forecast >= target and remaining == 0:
         print("Success: Target achieved!")
    print(f"----------------------")
