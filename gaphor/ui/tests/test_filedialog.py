import os
from pathlib import Path

import pytest
from gi.repository import Gio, Gtk

from gaphor.ui.filedialog import open_file_dialog, pretty_path, save_file_dialog


class TaskMock:
    def __init__(self, error=False):
        self._error = error

    def had_error(self):
        return self._error


class FileDialogMock(Gtk.FileDialog):
    def __init__(self):
        super().__init__()
        self._save_response = Gio.File.parse_name("/unset")
        self._error = False
        self.calls = {
            "save": 0,
            "open": 0,
            "open_finish": 0,
            "open_multiple": 0,
            "open_multiple_finish": 0,
        }

    # async def open(self, parent):
    #     return self._save_response

    # async def open_multiple(self, parent):
    #     return self._save_response

    async def save(self, parent):
        self.calls["save"] += 1
        return self._save_response
 
    def open(self, parent, cancellable, callback):
        self.calls["open"] += 1
        self.save_callback = callback
        callback(self, TaskMock(self._error))

    def open_finish(self, result):
        self.calls["open_finish"] += 1
        return self._save_response

    def open_multiple(self, parent, cancellable, callback):
        self.calls["open_multiple"] += 1
        self.save_callback = callback
        callback(self, TaskMock(self._error))

    def open_multiple_finish(self, result):
        self.calls["open_multiple_finish"] += 1
        return self._save_response
 
    def define_response(self, response):
        if isinstance(response, list):
            self._save_response = Gio.ListStore(item_type=Gio.File)
            for r in response:
                self._save_response.append(Gio.File.parse_name(r))
        else:
            self._save_response = Gio.File.parse_name(response)

    def define_error(self, error):
        self._error = error


@pytest.fixture
def file_dialog(monkeypatch):
    stub = FileDialogMock()

    def new_file_dialog():
        return stub

    monkeypatch.setattr("gi.repository.Gtk.FileDialog.new", new_file_dialog)
    return stub


@pytest.mark.asyncio
async def test_save_dialog(file_dialog):
    file_dialog.define_response("/test/path/model.gaphor")
    selected_file = await save_file_dialog(
        "title",
        Path("testfile.gaphor"),
        filters=[],
    )

    assert file_dialog.calls["save"] == 1
    assert selected_file.parts == (os.path.sep, "test", "path", "model.gaphor")


@pytest.mark.asyncio
async def test_save_dialog_with_full_file_name(file_dialog):
    filename = Path("/test/path/model.gaphor")
    await save_file_dialog(
        "title",
        filename,
        filters=[],
    )

    assert file_dialog.get_initial_name() == filename.name


@pytest.mark.asyncio
async def test_save_dialog_filename_without_extension(file_dialog):
    file_dialog.define_response("/test/path/model")
    selected_file = await save_file_dialog(
        "title",
        Path("model"),
        filters=[],
    )

    assert selected_file.parts == (os.path.sep, "test", "path", "model")


def test_open_dialog_single_cancelled(file_dialog):
    file_dialog.define_response("/test/path/file")
    file_dialog.define_error(True)
    selected_file = None

    def open_handler(f):
        nonlocal selected_file
        selected_file = f

    open_file_dialog("title", open_handler, multiple=False)

    assert file_dialog.calls["open"] == 1
    assert file_dialog.calls["open_finish"] == 0
    assert selected_file is None


def test_open_dialog_one_file_single(file_dialog):
    file_dialog.define_response("/test/path/file")
    selected_file = None

    def open_handler(f):
        nonlocal selected_file
        selected_file = f

    open_file_dialog(
        "title",
        open_handler,
        multiple=False,
    )

    assert file_dialog.calls["open"] == 1
    assert file_dialog.calls["open_finish"] == 1
    assert isinstance(selected_file, Path)
    assert selected_file.parts == (os.path.sep, "test", "path", "file")


def test_open_dialog_multiple_cancelled(file_dialog):
    file_dialog.define_response(["/test/path/file"])
    file_dialog.define_error(True)
    selected_file = None

    def open_handler(f):
        nonlocal selected_file
        selected_file = f

    open_file_dialog(
        "title",
        open_handler,
    )

    assert file_dialog.calls["open_multiple"] == 1
    assert file_dialog.calls["open_multiple_finish"] == 0
    assert selected_file is None


def test_open_dialog_one_file_multiple(file_dialog):
    file_dialog.define_response(["/test/path/file"])
    selected_file = None

    def open_handler(f):
        nonlocal selected_file
        selected_file = f

    open_file_dialog(
        "title",
        open_handler,
    )

    assert file_dialog.calls["open_multiple"] == 1
    assert file_dialog.calls["open_multiple_finish"] == 1
    assert isinstance(selected_file, list)
    assert len(selected_file) == 1
    assert isinstance(selected_file[0], Path)
    assert selected_file[0].parts == (os.path.sep, "test", "path", "file")


def test_format_home_folder():
    display_name = pretty_path(Path.home() / "folder" / "mymodel.gaphor")

    assert display_name.startswith("~")
    assert display_name.endswith("mymodel.gaphor")


@pytest.mark.skipif(not hasattr(os, "getuid"), reason="Only on Unix")
def test_format_portal_document():
    display_name = pretty_path(
        Path(f"/run/user/{os.getuid()}/doc/123abc/mymodel.gaphor")
    )

    assert display_name.startswith("mymodel.gaphor")
    assert display_name.endswith(")")
