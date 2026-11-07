"""`ops agent` command group."""

import click

from desktop_ops.commands.agent import run as run_cmd


@click.group()
def agent():
    """Agent commands."""


agent.add_command(run_cmd, name="run")