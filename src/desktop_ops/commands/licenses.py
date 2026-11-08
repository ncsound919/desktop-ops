"""`ops licenses` — dump third-party licenses."""

import click
import shutil
import subprocess
from rich.console import Console

console = Console()


@click.command()
def licenses():
    """Dump third-party licenses."""
    if shutil.which("pip-licenses"):
        subprocess.run(["pip-licenses"], check=False)
        return
    # Fallback: pip list
    console.print("[dim]pip-licenses not installed; showing pip list instead.[/dim]")
    subprocess.run(["python", "-m", "pip", "list"], check=False)