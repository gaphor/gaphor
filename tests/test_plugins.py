from gaphor.plugins import (
    manager,
    enable_plugins,
    default_plugin_path,
)
from gaphor.entrypoint import load_entry_points


def test_plugin_installation(tmp_path, monkeypatch):
    monkeypatch.setenv("GAPHOR_PLUGIN_PATH", str(tmp_path))

    parser = manager.parser()
    args = parser.parse_args(["install", "test-plugin/"])
    args.command(args)

    with enable_plugins(default_plugin_path()):
        entry_points = load_entry_points("gaphor.services")

    assert "test_plugin" in entry_points
