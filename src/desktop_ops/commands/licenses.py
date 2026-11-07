"""`ops licenses` — dump third-party licenses (placeholder)."""

import click
from rich.console import Console

console = Console()


@click.command()
def licenses():
    """Dump third-party licenses (placeholder)."""
    console.print("[dim]licenses: not yet implemented. Use pip-licenses / license-checker.[/dim]")