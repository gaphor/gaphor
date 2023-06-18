import sys

import pytest

from gaphor.plugins import (
    manager,
    enable_plugins,
    default_plugin_path,
)
from gaphor.entrypoint import load_entry_points


@pytest.fixture(autouse=True)
def install_test_plugin(tmp_path, monkeypatch):
    monkeypatch.setenv("GAPHOR_PLUGIN_PATH", str(tmp_path))

    parser = manager.parser()
    args = parser.parse_args(["install", "test-plugin/"])
    exit_code = args.command(args)

    assert exit_code == 0


def test_plugin_installed(tmp_path):
    with enable_plugins(default_plugin_path()):
        entry_points = load_entry_points("gaphor.services")

    assert "test_plugin" in entry_points


def test_sys_argv_is_not_changed():
    orig_argv = list(sys.argv)

    parser = manager.parser()
    args = parser.parse_args(["list"])
    args.command(args)

    assert sys.argv == orig_argv


def test_plugin_list(capsys):
    parser = manager.parser()
    args = parser.parse_args(["list"])
    args.command(args)

    out = capsys.readouterr().out

    assert "gaphor-test-plugin" in out


@pytest.mark.skip(reason="Uninstall does not work inside venv")
def test_plugin_uninstall(capsys):
    parser = manager.parser()
    args = parser.parse_args(["uninstall", "gaphor-test-plugin"])
    exit_code = args.command(args)

    out = capsys.readouterr().out

    assert "gaphor-test-plugin" in out
    assert exit_code == 0


def test_plugin_uninstall_unknown_package():
    parser = manager.parser()
    args = parser.parse_args(["uninstall", "unknown-gaphor-test-plugin"])
    exit_code = args.command(args)

    assert exit_code == 0
