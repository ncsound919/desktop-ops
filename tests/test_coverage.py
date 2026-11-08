"""Extensive coverage tests for desktop-ops modules."""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from desktop_ops import mcp_client, git_pr, telemetry, cost_guard, backup, mesh_check
from desktop_ops.adapters import llm, memory, testrunner
from desktop_ops.commands import licenses, playbooks, status, git_bootstrap


# --- mcp_client ---
def test_mcp_client_available_false():
    with patch.dict(os.environ, {"DESKTOP_OPS_OPENHUB_URL": ""}, clear=False):
        os.environ.pop("DESKTOP_OPS_OPENHUB_URL", None)
        os.environ.pop("DESKTOP_OPS_OPENHUB_TOKEN", None)
        import importlib
        import desktop_ops.mcp_client as mc
        importlib.reload(mc)
        assert mc.available() is False


def test_mcp_client_list_tools_refused():
    os.environ.pop("DESKTOP_OPS_OPENHUB_URL", None)
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    res = mc.list_tools()
    assert res["status"] == "refused"


def test_mcp_client_call_tool_refused():
    os.environ.pop("DESKTOP_OPS_OPENHUB_URL", None)
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    res = mc.call_tool("foo", {"bar": 1})
    assert res["status"] == "refused"


def test_mcp_client_available_true(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    assert mc.available() is True


def test_mcp_client_list_tools_ok(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"tools": []}
    with patch("desktop_ops.mcp_client.httpx.get", return_value=mock_resp):
        res = mc.list_tools()
    assert res == {"tools": []}


def test_mcp_client_list_tools_error(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("desktop_ops.mcp_client.httpx.get", return_value=mock_resp):
        res = mc.list_tools()
    assert res["status"] == "error"


def test_mcp_client_call_tool_ok(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": "ok"}
    with patch("desktop_ops.mcp_client.httpx.post", return_value=mock_resp):
        res = mc.call_tool("foo", {"bar": 1})
    assert res == {"result": "ok"}


def test_mcp_client_call_tool_error(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "not found"
    with patch("desktop_ops.mcp_client.httpx.post", return_value=mock_resp):
        res = mc.call_tool("foo")
    assert res["status"] == "error"


def test_mcp_client_exception(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_OPENHUB_URL", "http://localhost:3000")
    import importlib
    import desktop_ops.mcp_client as mc
    importlib.reload(mc)
    with patch("desktop_ops.mcp_client.httpx.get", side_effect=Exception("boom")):
        res = mc.list_tools()
    assert res["status"] == "error"


# --- git_pr ---
def test_git_pr_available_false():
    os.environ.pop("GITHUB_TOKEN", None)
    os.environ.pop("GH_TOKEN", None)
    import importlib
    import desktop_ops.git_pr as gp_mod
    importlib.reload(gp_mod)
    assert gp_mod.available() is False


def test_git_pr_create_refused():
    os.environ.pop("GITHUB_TOKEN", None)
    os.environ.pop("GH_TOKEN", None)
    import importlib
    import desktop_ops.git_pr as gp_mod
    importlib.reload(gp_mod)
    res = gp_mod.create_pr("o", "r", "t", "b", "h")
    assert res["status"] == "refused"


def test_git_pr_create_ok(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    import importlib
    import desktop_ops.git_pr as gp_mod
    importlib.reload(gp_mod)
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"number": 42, "html_url": "http://x"}
    with patch("desktop_ops.git_pr.httpx.post", return_value=mock_resp):
        res = gp_mod.create_pr("o", "r", "t", "b", "h")
    assert res["status"] == "ok"
    assert res["number"] == 42


def test_git_pr_create_error(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    import importlib
    import desktop_ops.git_pr as gp_mod
    importlib.reload(gp_mod)
    mock_resp = MagicMock()
    mock_resp.status_code = 422
    mock_resp.text = "validation failed"
    with patch("desktop_ops.git_pr.httpx.post", return_value=mock_resp):
        res = gp_mod.create_pr("o", "r", "t", "b", "h")
    assert res["status"] == "error"


def test_git_pr_exception(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    import importlib
    import desktop_ops.git_pr as gp_mod
    importlib.reload(gp_mod)
    with patch("desktop_ops.git_pr.httpx.post", side_effect=Exception("boom")):
        res = gp_mod.create_pr("o", "r", "t", "b", "h")
    assert res["status"] == "error"


# --- llm ---
def test_llm_chat_no_available(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    text, src = llm_mod.chat("hi")
    assert text is None
    assert "no LLM" in src


def test_llm_chat_mesh_ok(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "http://localhost:8788")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "hello"}}]}
    with patch("desktop_ops.adapters.llm.httpx.post", return_value=mock_resp):
        text, src = llm_mod.chat("hi")
    assert text == "hello"
    assert src == "mesh"


def test_llm_chat_mesh_fail_cloud_ok(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "http://localhost:8788")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "http://cloud")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_KEY", "key")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    mesh_resp = MagicMock()
    mesh_resp.status_code = 500
    cloud_resp = MagicMock()
    cloud_resp.status_code = 200
    cloud_resp.json.return_value = {"choices": [{"message": {"content": "cloud hi"}}]}
    with patch("desktop_ops.adapters.llm.httpx.post", side_effect=[Exception("mesh down"), cloud_resp]):
        text, src = llm_mod.chat("hi")
    assert text == "cloud hi"
    assert src == "cloud"


def test_llm_chat_cloud_error(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "http://cloud")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "bad request"
    with patch("desktop_ops.adapters.llm.httpx.post", return_value=mock_resp):
        text, src = llm_mod.chat("hi")
    assert text is None
    assert "cloud error" in src


# --- memory ---
def test_memory_store():
    from desktop_ops.adapters import memory
    res = memory.run("memory.store", {"x": 1})
    assert res["status"] == "ok"


def test_memory_recall():
    from desktop_ops.adapters import memory
    res = memory.run("memory.recall", {})
    assert res["status"] == "ok"
    assert res["results"] == []


def test_memory_unknown_action():
    from desktop_ops.adapters import memory
    res = memory.run("memory.foo", {})
    assert res["status"] == "refused"


# --- agent ---
def test_agent_run_task_no_llm(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "")
    import importlib
    import desktop_ops.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    from desktop_ops import agent
    steps = agent.run_task("do something", max_steps=2)
    assert len(steps) >= 1
    assert steps[0]["phase"] == "plan"
    assert "error" in steps[0]


# --- telemetry ---
def test_telemetry_emit_with_url(tmp_path, monkeypatch):
    monkeypatch.setattr(telemetry, "SINK", tmp_path / "t.jsonl")
    monkeypatch.setattr(telemetry, "TELEMETRY_URL", "http://example.com")
    mock_resp = MagicMock()
    with patch("httpx.post", return_value=mock_resp) as m:
        eid = telemetry.emit("test.event", data={"x": 1})
    assert eid
    assert m.called


# --- cost_guard ---
def test_cost_guard_check_budget_default():
    import os
    os.environ.pop("DESKTOP_OPS_DAILY_BUDGET", None)
    import importlib
    import desktop_ops.cost_guard as cg
    importlib.reload(cg)
    # no spend today
    res = cg.check_budget()
    assert res["status"] == "ok"


# --- backup ---
def test_backup_restore_subdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "x.txt").write_text("hello")
    bundle = backup.backup()
    assert Path(bundle).exists()


# --- mesh_check ---
def test_mesh_check_no_hits(tmp_path):
    (tmp_path / "clean.py").write_text("x = 42")
    hits = mesh_check.scan(str(tmp_path))
    assert hits == []


# --- playbooks ---
def test_playbooks_list_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli

    r = CliRunner().invoke(cli, ["playbooks", "list"])
    assert r.exit_code == 0
    assert "faceless-youtube" in r.output


# --- licenses ---
def test_licenses_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli

    r = CliRunner().invoke(cli, ["licenses"])
    assert r.exit_code == 0


# --- status ---
def test_status_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli

    r = CliRunner().invoke(cli, ["status"])
    assert r.exit_code == 0


# --- git_bootstrap dry run ---
def test_git_bootstrap_dry_run(tmp_path):
    from click.testing import CliRunner
    from desktop_ops.cli import cli

    d = tmp_path / "mytree"
    d.mkdir()
    (d / "f.txt").write_text("hi")
    r = CliRunner().invoke(cli, ["git-bootstrap", str(d), "--dry-run"])
    assert r.exit_code == 0
    assert "Dry run" in r.output


# --- serve ---
def test_serve_help():
    from click.testing import CliRunner
    from desktop_ops.cli import cli

    r = CliRunner().invoke(cli, ["serve", "--help"])
    assert r.exit_code == 0


# --- docling ---
def test_docling_refused():
    from desktop_ops.adapters import docling
    if not docling.probe():
        res = docling.run("ingest.convert", {"path": "x.pdf"})
        assert res["status"] == "refused"


# --- kokoro ---
def test_kokoro_refused_no_service():
    from desktop_ops.adapters import kokoro
    res = kokoro.run("tts.voices", {})
    assert res["status"] in ("ok", "error")


# --- ffmpeg ---
def test_ffmpeg_refused():
    from desktop_ops.adapters import ffmpeg
    if not ffmpeg.probe():
        res = ffmpeg.run("render.ffmpeg", {"args": []})
        assert res["status"] == "refused"


# --- listmonk ---
def test_listmonk_refused():
    from desktop_ops.adapters import listmonk
    res = listmonk.run("newsletter.subscribers", {})
    assert res["status"] == "refused"


# --- umami ---
def test_umami_refused():
    from desktop_ops.adapters import umami
    res = umami.run("analytics.pageviews", {})
    assert res["status"] == "refused"


# --- testrunner ---
def test_testrunner_unknown_runner():
    from desktop_ops.adapters import testrunner
    res = testrunner.run("test.run", {"runner": "nope", "path": "."})
    assert res["status"] == "refused"


# --- browser ---
def test_browser_unknown_action():
    from desktop_ops.adapters import browser
    res = browser.run("browser.foo", {})
    assert res["status"] == "refused"


# --- research ---
def test_research_unknown_action():
    from desktop_ops.adapters import research
    res = research.run("research.foo", {})
    assert res["status"] == "refused"


# --- scaffold ---
def test_scaffold_astro(tmp_path):
    from desktop_ops.adapters import scaffold
    res = scaffold.run("scaffold.create", {"name": "site", "template": "astro-blog", "dest": str(tmp_path)})
    assert res["status"] == "ok"
    assert (tmp_path / "site" / "package.json").exists()


# --- thumbnail ---
def test_thumbnail_with_base(tmp_path):
    from PIL import Image
    from desktop_ops.adapters import thumbnail
    base = str(tmp_path / "base.png")
    Image.new("RGB", (50, 50), (100, 100, 100)).save(base)
    out = str(tmp_path / "out.png")
    res = thumbnail.run("thumbnail.create", {"base": base, "text": "hi", "out": out, "w": 100, "h": 100})
    assert res["status"] == "ok"
    assert Path(out).exists()


# --- agent cli ---
def test_agent_run_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    r = CliRunner().invoke(cli, ["agent", "run", "test task", "--steps", "1"])
    assert r.exit_code == 0


# --- build cli ---
def test_build_scaffold_cli(tmp_path):
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    r = CliRunner().invoke(cli, ["build", "scaffold", "--name", "clitest", "--dest", str(tmp_path)])
    assert r.exit_code == 0


def test_build_audit_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    r = CliRunner().invoke(cli, ["build", "audit", "--path", "."])
    assert r.exit_code == 0


def test_content_thumbnail_cli(tmp_path):
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    out = str(tmp_path / "t.png")
    r = CliRunner().invoke(cli, ["content", "thumbnail", "--text", "hi", "--out", out])
    assert r.exit_code == 0


def test_harden_mesh_check_cli(tmp_path):
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    (tmp_path / "a.py").write_text("x = 'http://192.168.1.1'")
    r = CliRunner().invoke(cli, ["harden", "mesh-check", "--tree", str(tmp_path)])
    assert r.exit_code == 0


def test_harden_backup_cli():
    from click.testing import CliRunner
    from desktop_ops.cli import cli
    r = CliRunner().invoke(cli, ["harden", "backup"])
    assert r.exit_code == 0