"""CLI smoke tests."""

from click.testing import CliRunner
from desktop_ops.cli import cli


def test_cli_help():
    r = CliRunner().invoke(cli, ["--help"])
    assert r.exit_code == 0
    assert "Desktop Ops" in r.output


def test_doctor_runs():
    r = CliRunner().invoke(cli, ["doctor"])
    assert r.exit_code == 0


def test_adapters_runs():
    r = CliRunner().invoke(cli, ["adapters"])
    assert r.exit_code == 0


def test_build_templates():
    r = CliRunner().invoke(cli, ["build", "templates"])
    assert r.exit_code == 0
    assert "python-cli" in r.output


def test_harden_cost_check():
    r = CliRunner().invoke(cli, ["harden", "cost-check"])
    assert r.exit_code == 0