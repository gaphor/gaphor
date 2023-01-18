import logging

from gaphor.ui import main


def test_self_test(caplog):
    caplog.set_level(logging.INFO)
    exit_code = main(["--self-test"])

    assert exit_code == 0, caplog.text
