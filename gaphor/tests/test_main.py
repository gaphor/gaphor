import logging
import sys
from pathlib import Path

import pytest

import gaphor.ui
from gaphor.main import main


@pytest.fixture
def app_name():
    return sys.argv[0]


@pytest.fixture(autouse=True)
def mock_gaphor_ui_run(monkeypatch):
    _argv = []

    def run(argv):
        _argv[:] = argv
        return 0

    monkeypatch.setattr(gaphor.ui, "run", run)
    return _argv


def test_run_main(app_name):
    exit_code = main([app_name])

    assert exit_code == 0


def test_version(capsys, app_name):
    with pytest.raises(SystemExit):
        main([app_name, "-V"])

    assert "Gaphor" in capsys.readouterr().out


def test_debug_logging(app_name):
    main([app_name, "-v"])

    assert logging.getLogger("gaphor").getEffectiveLevel() == logging.DEBUG


def test_quiet_logging(app_name):
    main([app_name, "-q"])

    assert logging.getLogger("root").getEffectiveLevel() == logging.WARNING


def test_self_test(mock_gaphor_ui_run, app_name):
    main([app_name, "--self-test"])

    assert mock_gaphor_ui_run == [app_name, "--self-test"]


def test_gapplication_service(mock_gaphor_ui_run, app_name):
    main([app_name, "--gapplication-service"])

    assert mock_gaphor_ui_run == [app_name, "--gapplication-service"]


def test_run_script(capsys, app_name):
    run_script = Path(__file__).parent / "run_script.py"

    main([app_name, "exec", str(run_script)])

    assert "Running a test script for Gaphor" in capsys.readouterr().out
