import subprocess
import sys
from pathlib import Path
from urllib import error, request

import pytest

from gaphor.entrypoint import load_entry_points
from gaphor.plugins import (
    default_plugin_path,
    enable_plugins,
)


def have_internet():
    try:
        request.urlopen("http://gaphor.org", timeout=1)
    except error.URLError:
        return False
    else:
        return True


@pytest.mark.skipif(not have_internet(), reason="This test requires access to pypi")
def test_loading_plugins(tmp_path, monkeypatch):
    monkeypatch.setenv("GAPHOR_PLUGIN_PATH", str(tmp_path))

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(tmp_path),
            Path(__file__).parent.parent / "test-plugin",
        ],
        check=True,
    )

    with enable_plugins(default_plugin_path()):
        entry_points = load_entry_points("gaphor.services")

    assert "test_plugin" in entry_points
