"""`ops git bootstrap` — initialize git in an unversioned tree (human-approved)."""

import subprocess
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command("git-bootstrap")
@click.argument("tree_path", type=click.Path(exists=True, file_okay=False))
@click.option("--dry-run", is_flag=True, help="Show what would happen without doing it.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def git_bootstrap(tree_path, dry_run, yes):
    """Initialize git in an unversioned tree and create an initial commit.

    Always starts with a dry-run summary. Requires explicit confirmation unless
    --dry-run is passed (which never commits).
    """
    p = Path(tree_path).resolve()
    git_dir = p / ".git"
    if git_dir.exists():
        console.print(f"[yellow]{p} already has .git — skipping.[/yellow]")
        return

    # Heavy dirs to skip in counting (node_modules, build artifacts, etc.)
    SKIP = {".git", "node_modules", ".gradle", "build", "dist", ".expo",
            ".next", "out", "target", "__pycache__", ".venv", "venv"}

    def _is_skipped(path):
        return any(part in SKIP for part in path.relative_to(p).parts)

    files = [f for f in p.rglob("*") if f.is_file() and not _is_skipped(f)]
    console.print(f"Target: {p}")
    console.print(f"Files to commit (excluding heavy dirs): {len(files)}")

    if dry_run:
        console.print("[dim]Dry run — no changes made.[/dim]")
        return

    if not yes:
        if not click.confirm("Proceed with git init + initial commit?", default=False):
            console.print("Aborted.")
            return

    # Ensure a .gitignore exists so heavy dirs are never committed
    gi = p / ".gitignore"
    if not gi.exists():
        gi.write_text(
            "node_modules/\n.gradle/\nbuild/\ndist/\n.expo/\n.next/\nout/\n"
            "target/\n__pycache__/\n.venv/\nvenv/\n*.log\nlocal.properties\n"
            ".env\n.env.*\n!.env.example\ndebug.keystore\n*.jks\n*.keystore\n"
        )
        console.print("[dim]Created default .gitignore[/dim]")

    subprocess.run(["git", "init"], cwd=p, check=True)
    subprocess.run(["git", "add", "-A"], cwd=p, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initial commit (desktop-ops git-bootstrap)"],
        cwd=p,
        check=True,
    )
    console.print(f"[green]Bootstrapped {p}[/green]")