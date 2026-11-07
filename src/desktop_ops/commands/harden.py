"""`ops harden` command group (Phase 5)."""

import click

from desktop_ops import mesh_check, cost_guard, backup


@click.group()
def harden():
    """Hardening commands."""


@harden.command("mesh-check")
@click.option("--tree", required=True)
def mesh_check_cmd(tree):
    hits = mesh_check.scan(tree)
    click.echo({"hits": len(hits), "sample": hits[:10]})


@harden.command("cost-check")
def cost_check_cmd():
    click.echo(cost_guard.check_budget())


@harden.command("backup")
def backup_cmd():
    click.echo({"bundle": backup.backup()})


@harden.command("restore")
@click.option("--path", default=None)
def restore_cmd(path):
    click.echo(backup.restore(path))