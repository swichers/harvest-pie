import re
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

def hex_to_ansi(hex_color):
    """
    Simplest possible hex to ANSI escape.
    """
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return f"\033[38;2;{r};{g};{b}m"
    except Exception:
        return ""

def strip_legend(chart_str):
    """
    Strips the built-in legend from term_piechart output.
    It looks for the bullet and removes everything from there to the end of the line.
    """
    lines = []
    # Regex to match the bullet (possibly with ANSI codes) and everything after
    pattern = re.compile(r'\s*\x1b\[[0-9;]*m•\x1b\[[0-9;]*m\s+.*$')
    
    for line in chart_str.splitlines():
        # Remove the legend part
        cleaned = pattern.sub('', line)
        lines.append(cleaned.rstrip())
    return lines

def render_pie_chart(stats, config=None):
    worked = stats['worked']
    remaining = stats['remaining']
    gap = stats.get('gap', 0.0)
    billable_worked = stats.get('billable_worked', 0.0)
    billable_target = stats.get('billable_target', 0.0)
    
    if config is None:
        config = {}
        
    # Modern Professional UX Palette
    color_worked = config.get('color_worked', '#144620')
    color_remaining = config.get('color_remaining', '#6E4A02')
    color_under_target = config.get('color_under_target', '#8E201C')
    
    # Highlighted versions
    h_worked = highlight_color(color_worked)
    h_remaining = highlight_color(color_remaining)
    h_gap = highlight_color(color_under_target)
    
    # Progress ratio based on billable target
    progress_ratio = 0.0
    if billable_target > 0:
        progress_ratio = min(1.0, billable_worked / billable_target)
    
    original_slices = []
    if worked > 0:
        original_slices.append({"name": "Worked", "value": worked, "color": color_worked, "h_color": h_worked})
    if remaining > 0:
        original_slices.append({"name": "Remaining", "value": remaining, "color": color_remaining, "h_color": h_remaining})
    if gap > 0:
        original_slices.append({"name": "Gap", "value": gap, "color": color_under_target, "h_color": h_gap})
    
    total_value = sum(s['value'] for s in original_slices)
    if total_value == 0:
        return

    bright_threshold = total_value * progress_ratio
    
    # Split data for the actual pie chart rendering
    pie_data = []
    current_total = 0.0
    for s in original_slices:
        val = s['value']
        color = s['color']
        h_color = s['h_color']
        name = s['name']
        
        if current_total + val <= bright_threshold:
            pie_data.append({"name": name, "value": val, "color": h_color})
        elif current_total < bright_threshold:
            bright_part = bright_threshold - current_total
            normal_part = val - bright_part
            pie_data.append({"name": name, "value": bright_part, "color": h_color})
            pie_data.append({"name": name, "value": normal_part, "color": color})
        else:
            pie_data.append({"name": name, "value": val, "color": color})
            
        current_total += val

    # Create pie chart and strip its legend
    try:
        pie = Pie(pie_data, radius=10)
        chart_str = pie.render()
        
        chart_only_lines = strip_legend(chart_str)
        # Calculate visible width for proper alignment
        max_chart_width = max(len(re.sub(r'\x1b\[[0-9;]*m', '', l)) for l in chart_only_lines) if chart_only_lines else 0
        
        # Build our own unified legend
        reset = "\033[0m"
        legend_lines = []
        for s in original_slices:
            name = s['name']
            val = s['value']
            c_norm = hex_to_ansi(s['color'])
            c_high = hex_to_ansi(s['h_color'])
            perc = (val / total_value) * 100
            # Side-by-side bullets: highlight and normal
            bullet = f"{c_high}•{c_norm}•{reset}"
            legend_lines.append(f"{bullet} {name} {perc:.2f}% ({val:.2f} hrs)")
            
        # Combine chart and legend
        output = []
        mid = len(chart_only_lines) // 2
        start_leg = max(0, mid - len(legend_lines) // 2)
        
        for i, chart_line in enumerate(chart_only_lines):
            legend_part = ""
            leg_idx = i - start_leg
            if 0 <= leg_idx < len(legend_lines):
                legend_part = "    " + legend_lines[leg_idx]
            
            # Align legend by padding chart_line (considering ANSI codes for length)
            visible_len = len(re.sub(r'\x1b\[[0-9;]*m', '', chart_line))
            padding = " " * (max_chart_width - visible_len)
            output.append(chart_line + padding + legend_part)
            
        print("\n" + "\n".join(output))
        
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
