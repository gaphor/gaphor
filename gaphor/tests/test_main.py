import logging

import pytest

import gaphor.ui
from gaphor.main import main

APP_NAME = "/path/to/gaphor"


@pytest.fixture(autouse=True)
def mock_gaphor_ui_run(monkeypatch):
    _argv = []

    def run(argv):
        _argv[:] = argv
        return 0

    monkeypatch.setattr(gaphor.ui, "run", run)
    return _argv


def test_run_main():
    exit_code = main([APP_NAME])

    assert exit_code == 0


def test_version(capsys):
    main([APP_NAME, "-v"])

    assert "Gaphor" in capsys.readouterr().out


def test_debug_logging():
    main([APP_NAME, "-d"])

    assert logging.getLogger("gaphor").getEffectiveLevel() == logging.DEBUG


def test_quiet_logging():
    main([APP_NAME, "-q"])

    assert logging.getLogger("root").getEffectiveLevel() == logging.WARNING


def test_self_test(mock_gaphor_ui_run):
    main([APP_NAME, "--self-test"])

    assert mock_gaphor_ui_run == [APP_NAME, "--self-test"]


def test_gapplication_service(mock_gaphor_ui_run):
    main([APP_NAME, "--gapplication-service"])

    assert mock_gaphor_ui_run == [APP_NAME, "--gapplication-service"]
