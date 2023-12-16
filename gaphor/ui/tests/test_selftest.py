import logging

from gaphor.ui import run


def test_self_test(caplog):
    caplog.set_level(logging.DEBUG)
    exit_code = run(["--self-test"])

    assert exit_code == 0
