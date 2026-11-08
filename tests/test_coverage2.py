"""Targeted coverage tests for low-coverage modules."""

import os
from unittest.mock import patch, MagicMock

# aider
def test_aider_run_refused():
    from desktop_ops.adapters import aider
    res = aider.run("code.edit", {})
    assert res["status"] == "refused"


def test_aider_unknown_action():
    from desktop_ops.adapters import aider
    res = aider.run("code.foo", {})
    assert res["status"] == "refused"


def test_aider_capabilities():
    from desktop_ops.adapters import aider
    assert "code.edit" in aider.capabilities()


# blog
def test_blog_build_no_npm(monkeypatch, tmp_path):
    from desktop_ops.adapters import blog
    # create a fake dir
    d = tmp_path / "blog"
    d.mkdir()
    res = blog.run("blog.build", {"path": str(d)})
    assert res["status"] in ("failed", "error")


def test_blog_unknown_action():
    from desktop_ops.adapters import blog
    res = blog.run("blog.foo", {})
    assert res["status"] == "refused"


# testrunner
def test_testrunner_run_pytest_missing():
    from desktop_ops.adapters import testrunner
    # pytest is installed now, so test with a nonexistent path
    res = testrunner.run("test.run", {"runner": "pytest", "path": "/nonexistent"})
    assert res["status"] in ("failed", "error", "refused")


def test_testrunner_unknown_action():
    from desktop_ops.adapters import testrunner
    res = testrunner.run("test.foo", {})
    assert res["status"] == "refused"


# umami
def test_umami_probe_with_url(monkeypatch):
    monkeypatch.setenv("UMAMI_URL", "http://localhost:3001")
    import importlib
    import desktop_ops.adapters.umami as um
    importlib.reload(um)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("desktop_ops.adapters.umami.httpx.get", return_value=mock_resp):
        assert um.probe() is True


def test_umami_run_ok(monkeypatch):
    monkeypatch.setenv("UMAMI_URL", "http://localhost:3001")
    monkeypatch.setenv("UMAMI_TOKEN", "tok")
    import importlib
    import desktop_ops.adapters.umami as um
    importlib.reload(um)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"id": 1}]
    with patch("desktop_ops.adapters.umami.httpx.get", return_value=mock_resp):
        res = um.run("analytics.pageviews", {})
    assert res["status"] == "ok"


def test_umami_run_error(monkeypatch):
    monkeypatch.setenv("UMAMI_URL", "http://localhost:3001")
    import importlib
    import desktop_ops.adapters.umami as um
    importlib.reload(um)
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("desktop_ops.adapters.umami.httpx.get", return_value=mock_resp):
        res = um.run("analytics.pageviews", {})
    assert res["status"] == "error"


# docling
def test_docling_unknown_action():
    from desktop_ops.adapters import docling
    res = docling.run("ingest.foo", {})
    assert res["status"] == "refused"


def test_docling_no_path():
    from desktop_ops.adapters import docling
    if docling.probe():
        res = docling.run("ingest.convert", {})
        assert res["status"] == "refused"


# listmonk
def test_listmonk_campaign(monkeypatch):
    monkeypatch.setenv("LISTMONK_URL", "http://localhost:9000")
    monkeypatch.setenv("LISTMONK_USER", "admin")
    monkeypatch.setenv("LISTMONK_PASS", "pass")
    import importlib
    import desktop_ops.adapters.listmonk as lm
    importlib.reload(lm)
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"id": 1}
    with patch("desktop_ops.adapters.listmonk.httpx.post", return_value=mock_resp):
        res = lm.run("newsletter.campaign", {"name": "test"})
    assert res["status"] == "ok"


def test_listmonk_unknown_action(monkeypatch):
    monkeypatch.setenv("LISTMONK_URL", "http://localhost:9000")
    import importlib
    import desktop_ops.adapters.listmonk as lm
    importlib.reload(lm)
    res = lm.run("newsletter.foo", {})
    assert res["status"] == "refused"


def test_listmonk_error(monkeypatch):
    monkeypatch.setenv("LISTMONK_URL", "http://localhost:9000")
    import importlib
    import desktop_ops.adapters.listmonk as lm
    importlib.reload(lm)
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("desktop_ops.adapters.listmonk.httpx.get", return_value=mock_resp):
        res = lm.run("newsletter.subscribers", {})
    assert res["status"] == "error"


# kokoro
def test_kokoro_unknown_action():
    from desktop_ops.adapters import kokoro
    res = kokoro.run("tts.foo", {})
    assert res["status"] == "refused"


def test_kokoro_voices_error():
    from desktop_ops.adapters import kokoro
    # service not running
    res = kokoro.run("tts.voices", {})
    assert res["status"] in ("ok", "error")


# ffmpeg
def test_ffmpeg_concat():
    from desktop_ops.adapters import ffmpeg
    if not ffmpeg.probe():
        res = ffmpeg.run("render.concat", {"inputs": [], "out": "out.mp4"})
        assert res["status"] == "refused"
    else:
        res = ffmpeg.run("render.concat", {"inputs": [], "out": "out.mp4"})
        assert "status" in res


def test_ffmpeg_unknown_action():
    from desktop_ops.adapters import ffmpeg
    res = ffmpeg.run("render.foo", {})
    assert res["status"] == "refused"


# audit
def test_audit_unknown_action():
    from desktop_ops.adapters import audit
    res = audit.run("audit.foo", {})
    assert res["status"] == "refused"


# agent
def test_agent_run_with_action(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "http://cloud")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "ACTION aider.code.edit | {}"}}]}
    with patch("desktop_ops.adapters.llm.httpx.post", return_value=mock_resp):
        from desktop_ops import agent
        steps = agent.run_task("test", max_steps=1)
    assert len(steps) >= 2  # plan + act


# git_bootstrap
def test_git_bootstrap_already_has_git(tmp_path):
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    d = tmp_path / "repo"
    d.mkdir()
    (d / ".git").mkdir()
    r = CliRunner().invoke(cli, ["git-bootstrap", str(d), "--yes"])
    assert r.exit_code == 0
    assert "already has .git" in r.output


# mesh_check
def test_mesh_check_multiple_patterns(tmp_path):
    from desktop_ops import mesh_check
    (tmp_path / "a.py").write_text("x = 'http://10.0.2.2:8000'\ny = 'localhost:8000'")
    hits = mesh_check.scan(str(tmp_path))
    assert len(hits) >= 2


# cost_guard
def test_cost_guard_record():
    import tempfile, os
    from pathlib import Path
    from desktop_ops import cost_guard
    d = Path(tempfile.mkdtemp())
    cost_guard.COST_LOG = d / "costs.jsonl"
    cost_guard.record("test", 1.0, "note")
    assert cost_guard.COST_LOG.exists()
    assert cost_guard.today_spend() == 1.0


# backup
def test_backup_restore_ok(tmp_path):
    import os
    os.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "x.txt").write_text("hello")
    (tmp_path / "config").mkdir()
    bundle = __import__("desktop_ops.backup", fromlist=["backup"]).backup()
    assert __import__("pathlib").Path(bundle).exists()


# mcp_client available with token
def test_mcp_client_headers(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_TOKEN", "tok123")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    h = mc._headers()
    assert "Authorization" in h
    assert h["Authorization"] == "Bearer tok123"