"""`ops doctor` — probe for required OSS tools."""

import shutil
import subprocess

import click
from rich.console import Console
from rich.table import Table

console = Console()

TOOLS = [
    ("python", "python", "--version", "runtime"),
    ("git", "git", "--version", "version control"),
    ("node", "node", "--version", "web tooling"),
    ("ffmpeg", "ffmpeg", "-version", "video/audio rendering"),
    ("aider", "aider", "--version", "coding agent"),
    ("playwright", "playwright", "--version", "browser automation"),
    ("semgrep", "semgrep", "--version", "audit"),
    ("qdrant", "qdrant", "--version", "vector store (optional)"),
    ("listmonk", "listmonk", "--version", "newsletter (optional)"),
    ("ollama", "ollama", "--version", "NOT used on desktop (no GPU)"),
]


def _probe(binary, flag):
    path = shutil.which(binary)
    if not path:
        return None, "MISSING"
    try:
        args = flag.split() if " " in flag else [flag]
        r = subprocess.run([binary] + args, capture_output=True, text=True, timeout=10)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        ver = out[0][:60] if out else "ok"
        return path, ver
    except Exception as e:
        return path, f"ERROR: {e}"


@click.command()
def doctor():
    """Probe for required OSS tools and report status."""
    table = Table(title="ops doctor — OSS tool probe")
    table.add_column("Tool", style="cyan")
    table.add_column("Binary")
    table.add_column("Status")
    table.add_column("Version / note")

    found = missing = 0
    for name, binary, flag, note in TOOLS:
        path, ver = _probe(binary, flag)
        if path is None:
            status = "[red]MISSING[/red]"
            missing += 1
        else:
            status = "[green]FOUND[/green]"
            found += 1
        table.add_row(name, binary, status, f"{ver}  ({note})")

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {found} found, {missing} missing.")
    console.print("[dim]Install hints: see MULTIFUNCTION_TOOL_PLAN.md section 3.[/dim]")