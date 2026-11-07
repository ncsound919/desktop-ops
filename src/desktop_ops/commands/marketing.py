"""`ops marketing` command group (Phase 4)."""

import click

from desktop_ops.adapters import blog, listmonk, umami


@click.group()
def marketing():
    """Marketing commands."""


@marketing.command("blog-init")
@click.option("--name", required=True)
def blog_init(name):
    click.echo(blog.run("blog.init", {"name": name}))


@marketing.command("blog-build")
@click.option("--path", default="./blog")
def blog_build(path):
    click.echo(blog.run("blog.build", {"path": path}))


@marketing.command("newsletter-subs")
def newsletter_subs():
    click.echo(listmonk.run("newsletter.subscribers", {}))


@marketing.command("analytics")
def analytics():
    click.echo(umami.run("analytics.pageviews", {}))