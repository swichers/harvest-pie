import click
from .config import get_config, is_configured, update_config
from .harvest import get_weekly_stats
from .renderer import render_pie_chart, render_summary
import sys

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Harvest Pie CLI - Weekly hours worked vs scheduled."""
    if ctx.invoked_subcommand is None:
        if not is_configured():
            click.echo("Error: Harvest API is not configured.")
            click.echo("Please run: harvest-pie config")
            sys.exit(1)
        
        try:
            config = get_config()
            stats = get_weekly_stats(config)
            render_summary(stats)
            render_pie_chart(stats, config)
        except Exception as e:
            click.echo(f"Error fetching data from Harvest: {e}")
            sys.exit(1)

@cli.command()
@click.option('--token', help='Harvest Personal Access Token')
@click.option('--account', help='Harvest Account ID')
@click.option('--forecast-account', help='Forecast Account ID')
@click.option('--forecast-token', help='Forecast Access Token (if different from Harvest)')
@click.option('--hours', type=float, default=None, help='Scheduled hours per week (manual override)')
@click.option('--default-capacity', type=float, default=None, help='Default weekly capacity fallback (default 30)')
@click.option('--color-worked', help='Hex color for worked hours (e.g. #89cff0)')
@click.option('--color-missing', help='Hex color for missing hours (e.g. #ff7f7f)')
def config(token, account, forecast_account, forecast_token, hours, default_capacity, color_worked, color_missing):
    """Configure Harvest and Forecast API access."""
    current_config = get_config()
    
    # Harvest Config
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

    if default_capacity is not None:
        update_config("default_capacity", default_capacity)

    if color_worked:
        update_config("color_worked", color_worked)
    
    if color_missing:
        update_config("color_missing", color_missing)
        
    click.echo("Configuration saved to config.json")

if __name__ == '__main__':
    cli()
