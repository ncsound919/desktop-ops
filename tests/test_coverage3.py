"""Additional coverage for low-coverage adapters and mcp_server."""

import json
import os
import subprocess
from unittest.mock import patch, MagicMock

from desktop_ops.adapters import ruff, ffmpeg, agent_browser, docling


def test_ruff_lint_check_mocked():
    mock_r = MagicMock(returncode=0, stdout="[]", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch("subprocess.run", return_value=mock_r):
        res = ruff.run("lint.check", {"path": "."})
    assert res["status"] == "ok"


def test_ruff_lint_fix_mocked():
    mock_r = MagicMock(returncode=0, stdout="fixed", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch("subprocess.run", return_value=mock_r):
        res = ruff.run("lint.fix", {"path": "."})
    assert res["status"] == "ok"


def test_ruff_format_check_mocked():
    mock_r = MagicMock(returncode=1, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch("subprocess.run", return_value=mock_r):
        res = ruff.run("format.check", {"path": "."})
    assert res["status"] == "needs_format"


def test_ruff_format_fix_mocked():
    mock_r = MagicMock(returncode=0, stdout="formatted", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch("subprocess.run", return_value=mock_r):
        res = ruff.run("format.fix", {"path": "."})
    assert res["status"] == "ok"


def test_ruff_lint_check_issues():
    mock_r = MagicMock(returncode=1, stdout='[{"code":"E501"}]', stderr="")
    with patch("shutil.which", return_value="/usr/bin/ruff"), patch("subprocess.run", return_value=mock_r):
        res = ruff.run("lint.check", {"path": "."})
    assert res["status"] == "issues"
    assert res["count"] == 1


def test_ffmpeg_run_mocked():
    mock_r = MagicMock(returncode=0, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"), patch("subprocess.run", return_value=mock_r):
        res = ffmpeg.run("render.ffmpeg", {"args": ["-i", "in.mp4", "out.mp4"]})
    assert res["status"] == "ok"


def test_ffmpeg_concat_mocked():
    import tempfile, os
    d = tempfile.mkdtemp()
    inp = os.path.join(d, "in.txt")
    with open(inp, "w") as f:
        f.write("dummy")
    mock_r = MagicMock(returncode=0, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"), patch("subprocess.run", return_value=mock_r):
        res = ffmpeg.run("render.concat", {"inputs": ["a.mp4", "b.mp4"], "out": "out.mp4"})
    assert res["status"] == "ok"


def test_agent_browser_navigate_mocked():
    mock_r = MagicMock(returncode=0, stdout="navigated", stderr="")
    with patch("shutil.which", return_value="/usr/bin/agent-browser"), patch("subprocess.run", return_value=mock_r):
        res = agent_browser.run("browser.navigate", {"url": "https://example.com"})
    assert res["status"] == "ok"


def test_agent_browser_scrape_mocked():
    mock_r = MagicMock(returncode=0, stdout="content here", stderr="")
    with patch("shutil.which", return_value="/usr/bin/agent-browser"), patch("subprocess.run", return_value=mock_r):
        res = agent_browser.run("browser.scrape", {"url": "https://example.com"})
    assert res["status"] == "ok"


def test_agent_browser_screenshot_mocked():
    mock_r = MagicMock(returncode=0, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/agent-browser"), patch("subprocess.run", return_value=mock_r):
        res = agent_browser.run("browser.screenshot", {"url": "https://example.com", "out": "shot.png"})
    assert res["status"] == "ok"


def test_agent_browser_fill_mocked():
    mock_r = MagicMock(returncode=0, stdout="filled", stderr="")
    with patch("shutil.which", return_value="/usr/bin/agent-browser"), patch("subprocess.run", return_value=mock_r):
        res = agent_browser.run("browser.fill", {"selector": "#x", "value": "hi"})
    assert res["status"] == "ok"


def test_docling_unknown_action_covered():
    res = docling.run("ingest.foo", {})
    assert res["status"] == "refused"


# mcp_server
def test_mcp_server_404():
    import urllib.request, json
    import subprocess, time
    env = os.environ.copy()
    env["DESKTOP_OPS_PORT"] = "9877"
    p = subprocess.Popen(["python", "-m", "desktop_ops.mcp_server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    time.sleep(1.5)
    try:
        try:
            urllib.request.urlopen("http://127.0.0.1:9877/nonexistent")
        except urllib.error.HTTPError as e:
            assert e.code == 404
        # POST to bad path
        req = urllib.request.Request("http://127.0.0.1:9877/badpath", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            assert e.code == 404
        # POST to /mcp/call with bad name
        req = urllib.request.Request("http://127.0.0.1:9877/mcp/call", data=json.dumps({"name": "nope"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
            assert "error" in data
        except urllib.error.HTTPError as e:
            assert e.code == 400
    finally:
        p.terminate()
        p.wait()
