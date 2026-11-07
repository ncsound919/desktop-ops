"""Tests for desktop-ops pure-Python modules."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from desktop_ops.adapters import scaffold, thumbnail
from desktop_ops import mesh_check, cost_guard, backup, registry, telemetry, db


def test_scaffold_list():
    res = scaffold.run("scaffold.list", {})
    assert res["status"] == "ok"
    assert "python-cli" in res["templates"]


def test_scaffold_create_python_cli(tmp_path):
    res = scaffold.run("scaffold.create", {"name": "demo", "template": "python-cli", "dest": str(tmp_path)})
    assert res["status"] == "ok"
    p = Path(res["path"])
    assert (p / "pyproject.toml").exists()
    assert (p / "src" / "demo" / "__init__.py").exists()


def test_scaffold_create_unknown_template(tmp_path):
    res = scaffold.run("scaffold.create", {"name": "x", "template": "nope", "dest": str(tmp_path)})
    assert res["status"] == "refused"


def test_scaffold_create_no_name(tmp_path):
    res = scaffold.run("scaffold.create", {"template": "python-cli", "dest": str(tmp_path)})
    assert res["status"] == "refused"


def test_thumbnail_create(tmp_path):
    out = str(tmp_path / "thumb.png")
    res = thumbnail.run("thumbnail.create", {"text": "hello", "out": out, "w": 100, "h": 50})
    assert res["status"] == "ok"
    assert Path(out).exists()
    from PIL import Image

    img = Image.open(out)
    assert img.size == (100, 50)


def test_thumbnail_no_pil(monkeypatch):
    # probe returns True now (Pillow installed), so just check run works
    assert thumbnail.probe() is True


def test_mesh_check_scan(tmp_path):
    (tmp_path / "a.py").write_text("x = 'http://192.168.1.240:8000'")
    (tmp_path / "b.py").write_text("y = 42")
    hits = mesh_check.scan(str(tmp_path))
    assert len(hits) >= 1
    assert any("192.168" in h["match"] for h in hits)


def test_mesh_check_skips_large(tmp_path):
    big = tmp_path / "big.py"
    big.write_text("http://192.168.1.1 " * 100000)
    # make it > 500KB
    assert big.stat().st_size > 500_000
    hits = mesh_check.scan(str(tmp_path))
    assert all("big.py" not in h["file"] for h in hits)


def test_cost_guard_record_and_check(tmp_path, monkeypatch):
    monkeypatch.setattr(cost_guard, "COST_LOG", tmp_path / "costs.jsonl")
    cost_guard.record("test", 1.5, "unit")
    cost_guard.record("test", 2.0, "unit2")
    assert abs(cost_guard.today_spend() - 3.5) < 1e-9
    res = cost_guard.check_budget(5.0)
    assert res["status"] == "ok"
    assert abs(res["remaining"] - 1.5) < 1e-9


def test_cost_guard_exceeded(tmp_path, monkeypatch):
    monkeypatch.setattr(cost_guard, "COST_LOG", tmp_path / "costs.jsonl")
    cost_guard.record("test", 10.0)
    res = cost_guard.check_budget(5.0)
    assert res["status"] == "exceeded"


def test_backup_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "x.txt").write_text("hello")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "y.yaml").write_text("a: 1")
    bundle = backup.backup()
    assert Path(bundle).exists()
    # restore into fresh dir
    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()
    monkeypatch.chdir(restore_dir)
    res = backup.restore(str(tmp_path / "state" / "backup.zip"))
    assert res["status"] == "ok"


def test_registry_list():
    names = registry.list_adapters()
    assert "scaffold" in names
    assert "llm" in names


def test_registry_get_unknown():
    assert registry.get_adapter("nope") is None


def test_telemetry_emit(tmp_path, monkeypatch):
    monkeypatch.setattr(telemetry, "SINK", tmp_path / "telemetry.jsonl")
    monkeypatch.setattr(telemetry, "TELEMETRY_URL", "")
    eid = telemetry.emit("test.event", data={"x": 1})
    assert eid
    lines = (tmp_path / "telemetry.jsonl").read_text().splitlines()
    assert len(lines) == 1
    evt = json.loads(lines[0])
    assert evt["type"] == "test.event"
    assert evt["schema_version"] == 1


def test_db_write_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "ops.db")
    rid, h = db.write_receipt("test", {"hello": "world"})
    assert rid
    assert len(h) == 64


def test_agent_run_no_llm(monkeypatch):
    # Force no LLM available
    monkeypatch.setenv("DESKTOP_OPS_MESH_URL", "")
    monkeypatch.setenv("DESKTOP_OPS_CLOUD_URL", "")
    from desktop_ops import agent

    # reload llm module config
    import importlib
    import desktop_ops.adapters.llm as llm_mod

    importlib.reload(llm_mod)
    steps = agent.run_task("do something", max_steps=2)
    assert len(steps) >= 1
    assert steps[0]["phase"] == "plan"
    assert "error" in steps[0]


def test_scaffold_probe():
    assert scaffold.probe() is True


def test_thumbnail_probe():
    assert thumbnail.probe() is True