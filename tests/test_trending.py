"""Tests for trending-tool adapters."""

from desktop_ops.adapters import agent_browser, ruff, sherlock


def test_agent_browser_probe():
    assert isinstance(agent_browser.probe(), bool)


def test_agent_browser_capabilities():
    assert "browser.navigate" in agent_browser.capabilities()


def test_agent_browser_unknown_action():
    res = agent_browser.run("browser.foo", {})
    assert res["status"] == "refused"


def test_agent_browser_refused_when_not_installed():
    if not agent_browser.probe():
        res = agent_browser.run("browser.navigate", {"url": "https://example.com"})
        assert res["status"] == "refused"


def test_ruff_probe():
    assert isinstance(ruff.probe(), bool)


def test_ruff_capabilities():
    assert "lint.check" in ruff.capabilities()


def test_ruff_unknown_action():
    res = ruff.run("lint.foo", {})
    assert res["status"] == "refused"


def test_ruff_refused_when_not_installed():
    if not ruff.probe():
        res = ruff.run("lint.check", {"path": "."})
        assert res["status"] == "refused"


def test_sherlock_probe():
    assert isinstance(sherlock.probe(), bool)


def test_sherlock_capabilities():
    assert "osint.search_username" in sherlock.capabilities()


def test_sherlock_no_username():
    res = sherlock.run("osint.search_username", {})
    assert res["status"] == "refused"


def test_sherlock_unknown_action():
    res = sherlock.run("osint.foo", {})
    assert res["status"] == "refused"


def test_sherlock_refused_when_not_installed():
    if not sherlock.probe():
        res = sherlock.run("osint.search_username", {"username": "test"})
        assert res["status"] == "refused"