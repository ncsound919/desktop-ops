"""MCP server tests."""

import json
import subprocess
import time
import urllib.request

import pytest


@pytest.fixture
def server():
    import os
    env = os.environ.copy()
    env["DESKTOP_OPS_PORT"] = "9878"
    p = subprocess.Popen(
        ["python", "-m", "desktop_ops.mcp_server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    # Wait for server to be ready
    for _ in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen("http://127.0.0.1:9878/health", timeout=1)
            break
        except Exception:
            continue
    yield p
    p.terminate()
    p.wait()


def test_health(server):
    with urllib.request.urlopen("http://127.0.0.1:9878/health") as r:
        data = json.loads(r.read())
    assert data["status"] == "ok"


def test_tools_list(server):
    with urllib.request.urlopen("http://127.0.0.1:9878/mcp/tools") as r:
        data = json.loads(r.read())
    assert len(data["tools"]) > 0


def test_capabilities(server):
    with urllib.request.urlopen("http://127.0.0.1:9878/capabilities") as r:
        data = json.loads(r.read())
    assert "scaffold" in data


def test_mcp_call(server):
    req = urllib.request.Request(
        "http://127.0.0.1:9878/mcp/call",
        data=json.dumps({"name": "scaffold.scaffold.list", "params": {}}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    assert data["status"] == "ok"
