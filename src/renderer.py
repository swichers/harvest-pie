from term_piechart import Pie

def highlight_color(hex_color):
    """
    Creates a high-contrast highlight version of a color.
    Preserves the hue but pushes it to maximum vibrancy.
    """
    hex_color = hex_color.lstrip('#')
    try:
        rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        
        max_c = max(rgb)
        if max_c == 0:
            return "#666666"
            
        # Push to maximum vibrancy
        multiplier = 255 / max_c
        new_rgb = [min(255, int(c * multiplier)) for c in rgb]
        
        # If the result is still a bit dim (e.g. very dark base), 
        # boost it further toward white
        if sum(new_rgb) < 500:
             new_rgb = [min(255, int(c + (255 - c) * 0.2)) for c in new_rgb]

        return "#{:02x}{:02x}{:02x}".format(*new_rgb)
    except Exception:
        return f"#{hex_color}"

def render_pie_chart(stats, config=None):
    worked = stats['worked']
    remaining = stats['remaining']
    gap = stats.get('gap', 0.0)
    billable_worked = stats.get('billable_worked', 0.0)
    billable_target = stats.get('billable_target', 0.0)
    
    if config is None:
        config = {}
        
    # Modern Professional UX Palette
    # Success (Worked) -> Deep Emerald
    # Warning (Remaining) -> Deep Ochre/Amber
    # Error (Gap) -> Deep Crimson
    color_worked = config.get('color_worked', '#144620')
    color_remaining = config.get('color_remaining', '#6E4A02')
    color_under_target = config.get('color_under_target', '#8E201C')
    
    # Progress ratio based on billable target
    progress_ratio = 0.0
    if billable_target > 0:
        progress_ratio = min(1.0, billable_worked / billable_target)
    
    original_slices = []
    if worked > 0:
        original_slices.append({"name": "Worked", "value": worked, "color": color_worked})
    if remaining > 0:
        original_slices.append({"name": "Remaining", "value": remaining, "color": color_remaining})
    if gap > 0:
        original_slices.append({"name": "Gap", "value": gap, "color": color_under_target})
    
    total_value = sum(s['value'] for s in original_slices)
    bright_threshold = total_value * progress_ratio
    
    data = []
    current_total = 0.0
    for s in original_slices:
        val = s['value']
        color = s['color']
        bright_color = highlight_color(color)
        name = s['name']
        
        if current_total + val <= bright_threshold:
            # Whole slice is bright
            data.append({"name": f"{name} (B)", "value": val, "color": bright_color})
        elif current_total < bright_threshold:
            # Slice is partially bright
            bright_part = bright_threshold - current_total
            normal_part = val - bright_part
            data.append({"name": f"{name} (B)", "value": bright_part, "color": bright_color})
            data.append({"name": name, "value": normal_part, "color": color})
        else:
            # Whole slice is normal
            data.append({"name": name, "value": val, "color": color})
            
        current_total += val

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
