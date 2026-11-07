"""`ops status` — show desktop-ops state."""

import click
from rich.console import Console

console = Console()


@click.command()
def status():
    """Show desktop-ops status (placeholder)."""
    console.print("[bold]desktop-ops[/bold] v0.1.0")
    console.print("Phase 0 in progress. Run [cyan]ops doctor[/cyan] to check tools.")