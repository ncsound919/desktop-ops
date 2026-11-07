"""`ops adapters` — list registered adapters and their probe status."""

import click
from rich.console import Console
from rich.table import Table

from desktop_ops import registry

console = Console()


@click.command()
def adapters():
    """List registered adapters and probe status."""
    table = Table(title="Registered adapters")
    table.add_column("Name", style="cyan")
    table.add_column("Probe")
    table.add_column("Capabilities")
    for name in registry.list_adapters():
        mod = registry.get_adapter(name)
        ok = mod.probe() if hasattr(mod, "probe") else False
        caps = ", ".join(mod.capabilities()) if hasattr(mod, "capabilities") else "-"
        table.add_row(name, "[green]OK[/green]" if ok else "[red]MISSING[/red]", caps)
    console.print(table)