"""`ops build` command group."""

import click

from desktop_ops.adapters import scaffold, audit, testrunner
from desktop_ops import git_pr


@click.group()
def build():
    """Build-tool commands."""


@build.command("scaffold")
@click.option("--name", required=True)
@click.option("--template", default="python-cli")
@click.option("--dest", default=".")
def scaffold_cmd(name, template, dest):
    res = scaffold.run("scaffold.create", {"name": name, "template": template, "dest": dest})
    click.echo(res)


@build.command("templates")
def templates_cmd():
    res = scaffold.run("scaffold.list", {})
    click.echo(res)


@build.command("audit")
@click.option("--path", default=".")
def audit_cmd(path):
    res = audit.run("audit.scan", {"path": path})
    click.echo(res)


@build.command("test")
@click.option("--runner", default="pytest")
@click.option("--path", default=".")
def test_cmd(runner, path):
    res = testrunner.run("test.run", {"runner": runner, "path": path})
    click.echo(res)


@build.command("pr")
@click.option("--owner", required=True)
@click.option("--repo", required=True)
@click.option("--title", required=True)
@click.option("--head", required=True)
@click.option("--base", default="main")
@click.option("--body", default="")
def pr_cmd(owner, repo, title, head, base, body):
    res = git_pr.create_pr(owner, repo, title, body, head, base)
    click.echo(res)