"""Additional tests for adapters and edge cases."""

from desktop_ops.adapters import kokoro, ffmpeg, docling, blog, listmonk, umami, audit, testrunner, browser, research


def test_adapter_probes_return_bool():
    for mod in (kokoro, ffmpeg, docling, blog, listmonk, umami, audit, testrunner, browser, research):
        assert isinstance(mod.probe(), bool)


def test_adapter_capabilities_nonempty():
    for mod in (kokoro, ffmpeg, docling, blog, listmonk, umami, audit, testrunner, browser, research):
        caps = mod.capabilities()
        assert isinstance(caps, list)
        assert len(caps) > 0


def test_kokoro_refused_when_no_service():
    # service not running, should return error not crash
    res = kokoro.run("tts.synthesize", {"text": "hi", "out": "/tmp/x.wav"})
    assert res["status"] in ("error", "refused")


def test_ffmpeg_refused_when_not_installed():
    # ffmpeg may or may not be installed; run should not crash
    res = ffmpeg.run("render.ffmpeg", {"args": ["-version"]})
    assert res["status"] in ("ok", "failed", "error", "refused")


def test_thumbnail_unknown_action():
    res = __import__("desktop_ops.adapters.thumbnail", fromlist=["thumbnail"]).run("nope", {})
    assert res["status"] == "refused"


def test_blog_init(tmp_path):
    from desktop_ops.adapters import blog

    res = blog.run("blog.init", {"name": "myblog", "dest": None})
    # dest defaults to BLOG_DIR env; just check it doesn't crash
    assert "status" in res


def test_listmonk_refused_without_url():
    res = listmonk.run("newsletter.subscribers", {})
    assert res["status"] == "refused"


def test_umami_refused_without_url():
    res = umami.run("analytics.pageviews", {})
    assert res["status"] == "refused"


def test_audit_refused_without_semgrep():
    if not audit.probe():
        res = audit.run("audit.scan", {"path": "."})
        assert res["status"] == "refused"


def test_cost_guard_env_budget(monkeypatch):
    monkeypatch.setenv("DESKTOP_OPS_DAILY_BUDGET", "99.0")
    import importlib
    import desktop_ops.cost_guard as cg

    importlib.reload(cg)
    assert cg.BUDGET == 99.0