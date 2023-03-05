import pygit2
from pathlib import Path
from tempfile import TemporaryDirectory

from _pytest.monkeypatch import MonkeyPatch

from gaphor.ui import run
from gaphor.storage.tests.fixtures import create_merge_conflict


workspace = Path(__file__).parent.parent


def run_gaphor_with_merge_conflict():
    with TemporaryDirectory() as tmp_dir, MonkeyPatch.context() as monkeypatch:
        tmp_path = Path(tmp_dir)
        repo = pygit2.init_repository(tmp_path)

        create_merge_conflict(
            repo,
            tmp_path / "RAAML.gaphor",
            (workspace / "test-models" / "RAAML-original.gaphor").read_text(),
            (workspace / "models" / "RAAML.gaphor").read_text(),
            (workspace / "test-models" / "RAAML-incoming.gaphor").read_text(),
        )
        replace_merge_conflict_dialog(monkeypatch, "manual")

        run([__file__, str(tmp_path / "RAAML.gaphor")])


def replace_merge_conflict_dialog(monkeypatch, resolution):
    def mock_merge_conflict_dialog(_window, filename, handler):
        print("Shortcut merge conflict dialog:", filename)
        handler(resolution)

    monkeypatch.setattr(
        "gaphor.ui.filemanager.resolve_merge_conflict_dialog",
        mock_merge_conflict_dialog,
    )


if __name__ == "__main__":
    run_gaphor_with_merge_conflict()
