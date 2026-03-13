import click
from .config import get_config, is_configured, update_config
from .harvest import get_weekly_stats
from .renderer import render_pie_chart, render_summary
import sys

@click.group(invoke_without_command=True)
@click.option('--force-worked', type=float, help='Force worked hours (skip Harvest API)')
@click.option('--force-forecast', type=float, help='Force forecast hours (skip Forecast API)')
@click.pass_context
def cli(ctx, force_worked, force_forecast):
    """Harvest Pie CLI - Weekly hours worked vs scheduled."""
    if ctx.invoked_subcommand is None:
        if not is_configured():
            click.echo("Error: Harvest API is not configured.")
            click.echo("Please run: harvest-pie config")
            sys.exit(1)
        
        try:
            config = get_config()
            stats = get_weekly_stats(config, force_worked=force_worked, force_forecast=force_forecast)
            render_summary(stats)
            render_pie_chart(stats, config)
        except Exception as e:
            click.echo(f"Error fetching data: {e}")
            sys.exit(1)

@cli.command()
@click.option('--token', help='Harvest Personal Access Token')
@click.option('--account', help='Harvest Account ID')
@click.option('--forecast-account', help='Forecast Account ID')
@click.option('--forecast-token', help='Forecast Access Token (if different from Harvest)')
@click.option('--hours', type=float, default=None, help='Scheduled hours per week (manual override)')
@click.option('--target', type=float, default=None, help='Target hours per week (default 30)')
@click.option('--default-capacity', type=float, default=None, help='Default weekly capacity fallback (default 30)')
@click.option('--color-worked', help='Hex color for worked hours')
@click.option('--color-remaining', help='Hex color for remaining hours')
@click.option('--color-under-target', help='Hex color for under target hours')
def config(token, account, forecast_account, forecast_token, hours, target, default_capacity, color_worked, color_remaining, color_under_target):
    """Configure Harvest and Forecast API access."""
    current_config = get_config()
    
    # ... Harvest Config unchanged ...
    if not token and "access_token" not in current_config:
        token = click.prompt('Harvest Personal Access Token')
    if token:
        update_config("access_token", token)
        
    if not account and "account_id" not in current_config:
        account = click.prompt('Harvest Account ID')
    if account:
        update_config("account_id", account)

    # Forecast Config
    if not forecast_account and "forecast_account_id" not in current_config:
        forecast_account = click.prompt('Forecast Account ID', default='')
    if forecast_account:
        update_config("forecast_account_id", forecast_account)
    
    if forecast_token:
        update_config("forecast_token", forecast_token)
        
    if hours is not None:
        update_config("scheduled_hours", hours)

    if target is not None:
        update_config("target_hours", target)

    if default_capacity is not None:
        update_config("default_capacity", default_capacity)

    if color_worked:
        update_config("color_worked", color_worked)
    
    if color_remaining:
        update_config("color_remaining", color_remaining)

    if color_under_target:
        update_config("color_under_target", color_under_target)
        
    click.echo("Configuration saved to config.json")

if __name__ == '__main__':
    cli()
