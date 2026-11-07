"""`ops agent run <task>` — run a task through the agent loop."""

import click
import json
from rich.console import Console
from rich.syntax import Syntax

from desktop_ops import agent, telemetry

console = Console()


@click.command("run")
@click.argument("task")
@click.option("--steps", default=5, help="Max steps.")
def run(task, steps):
    """Run a task through the agent loop."""
    console.print(f"[bold]Task:[/bold] {task}")
    result = agent.run_task(task, max_steps=steps)
    console.print_json(json.dumps(result, indent=2, default=str))
    telemetry.emit("agent.run.completed", data={"task": task, "steps": len(result)})