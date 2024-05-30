import logging
import sys
from pathlib import Path

import pytest

import gaphor.ui
from gaphor.main import main

APP_NAME = sys.argv[0]


@pytest.fixture(autouse=True)
def mock_gaphor_ui_run(monkeypatch):
    _argv = []

    def run(argv, recover=False):
        _argv[:] = argv
        return 0

    monkeypatch.setattr(gaphor.ui, "run", run)
    return _argv


def test_run_main():
    exit_code = main([APP_NAME])

    assert exit_code == 0


def test_version(capsys):
    with pytest.raises(SystemExit):
        main([APP_NAME, "-V"])

    assert "Gaphor" in capsys.readouterr().out


def test_debug_logging():
    main([APP_NAME, "-v"])

    assert logging.getLogger("gaphor").getEffectiveLevel() == logging.DEBUG


def test_quiet_logging():
    main([APP_NAME, "-q"])

    assert logging.getLogger("root").getEffectiveLevel() == logging.WARNING


def test_gapplication_service(mock_gaphor_ui_run):
    main([APP_NAME, "--gapplication-service"])

    assert mock_gaphor_ui_run == [APP_NAME, "--gapplication-service"]


def test_run_script(capsys):
    run_script = Path(__file__).parent / "run_script.py"

    main([APP_NAME, "exec", str(run_script)])

    assert "Running a test script for Gaphor" in capsys.readouterr().out
