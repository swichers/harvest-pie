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
            render_pie_chart(stats)
        except Exception as e:
            click.echo(f"Error fetching data from Harvest: {e}")
            sys.exit(1)

@cli.command()
@click.option('--token', help='Harvest Personal Access Token')
@click.option('--account', help='Harvest Account ID')
@click.option('--hours', type=float, default=None, help='Scheduled hours per week')
def config(token, account, hours):
    """Configure Harvest API access."""
    current_config = get_config()
    
    if not token and "access_token" not in current_config:
        token = click.prompt('Harvest Personal Access Token')
    if token:
        update_config("access_token", token)
        
    if not account and "account_id" not in current_config:
        account = click.prompt('Harvest Account ID')
    if account:
        update_config("account_id", account)
        
    if hours is not None:
        update_config("scheduled_hours", hours)
        
    click.echo("Configuration saved to config.json")

if __name__ == '__main__':
    cli()
