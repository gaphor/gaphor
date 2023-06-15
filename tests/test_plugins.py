import subprocess
import sys
from pathlib import Path

from gaphor.plugins import (
    enable_plugins,
    default_plugin_path,
)
from gaphor.entrypoint import load_entry_points


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
        ]
    )

    with enable_plugins(default_plugin_path()):
        entry_points = load_entry_points("gaphor.services")

    assert "test_plugin" in entry_points
