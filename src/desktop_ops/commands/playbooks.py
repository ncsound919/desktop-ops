"""`ops playbooks` command group."""

import click
from pathlib import Path
import yaml

from rich.console import Console

console = Console()


@click.group()
def playbooks():
    """Playbook commands."""


@playbooks.command("list")
def list_cmd():
    d = Path("config/playbooks")
    if not d.exists():
        console.print("No playbooks directory.")
        return
    for f in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text())
            console.print(f"- {f.stem}: stage={data.get('stage')}, risk={data.get('risk')}, enabled={data.get('enabled')}")
        except Exception as e:
            console.print(f"- {f.stem}: ERROR {e}")