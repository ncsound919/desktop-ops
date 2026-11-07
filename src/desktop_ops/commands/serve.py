"""`ops serve` — start the MCP server."""

import click

from desktop_ops import mcp_server


@click.command()
@click.option("--port", default=None, type=int)
def serve(port):
    """Start the desktop-ops MCP server."""
    mcp_server.serve(port)