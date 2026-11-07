"""CLI entry point: `ops <command>`."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def cli():
    """Desktop Ops — desktop execution plane for the overlay365 ecosystem."""


# Register subcommands
from desktop_ops.commands import doctor, status, git_bootstrap, licenses, adapters, agent_group, build, content, marketing, harden, playbooks, serve  # noqa: E402

cli.add_command(doctor.doctor)
cli.add_command(status.status)
cli.add_command(git_bootstrap.git_bootstrap)
cli.add_command(licenses.licenses)
cli.add_command(adapters.adapters)
cli.add_command(agent_group.agent)
cli.add_command(build.build)
cli.add_command(content.content)
cli.add_command(marketing.marketing)
cli.add_command(harden.harden)
cli.add_command(playbooks.playbooks)
cli.add_command(serve.serve)


def main():
    cli()


if __name__ == "__main__":
    main()