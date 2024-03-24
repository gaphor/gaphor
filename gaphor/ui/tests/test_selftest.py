import logging
import os
import sys

from gaphor.ui import run


def test_self_test(caplog):
    caplog.set_level(logging.DEBUG)
    exit_code = run(argv=[], launch_service="self_test")

    # Self test tends to fail every now and then on macOS.
    # We have the same issue for the final package check,
    # but a retry normally fixes it.
    # So let's retry on GitHub Actions on macOS only.
    if exit_code != 0 and sys.platform == "darwin" and os.getenv("CI"):
        exit_code = run(argv=[], launch_service="self_test")

    assert exit_code == 0
