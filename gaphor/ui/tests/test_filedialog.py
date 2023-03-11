import os.path
from pathlib import Path

import pytest
from gi.repository import Gio, Gtk

from gaphor.ui.filedialog import save_file_dialog


class FileChooserStub:
    def __init__(self) -> None:
        self._response_callback = None
        self._current_name = None
        self._current_folder = None

    @property
    def stub_current_name(self):
        return self._current_name

    @property
    def stub_current_folder(self):
        return self._current_folder

    def stub_select_file(self, folder, name):
        self._current_folder = folder
        self._current_name = name
        assert self._response_callback
        self._response_callback(self, Gtk.ResponseType.ACCEPT)

    def connect(self, signal, callback):
        assert signal == "response"
        self._response_callback = callback

    def get_file(self):
        return Gio.File.new_for_path(self._current_folder).get_child(self._current_name)

    def set_current_name(self, name: str):
        self._current_name = name

    def set_current_folder(self, name: Gio.File):
        self._current_folder = name.get_parse_name()

    def add_filter(self, filter):
        pass

    def set_modal(self, modal):
        pass

    def show(self):
        pass

    def destroy(self):
        pass


@pytest.fixture
def file_chooser(monkeypatch):
    stub = FileChooserStub()

    def new_file_chooser(title, parent, action, accept_label, cancel_label):
        return stub

    monkeypatch.setattr("gi.repository.Gtk.FileChooserNative.new", new_file_chooser)
    return stub


def test_save_dialog(file_chooser):
    selected_file = None

    def save_handler(f):
        nonlocal selected_file
        selected_file = f

    save_file_dialog(
        "title",
        save_handler,
        filename=None,
        extension=".gaphor",
        filters=[],
    )

    file_chooser.stub_select_file("/test/path", "model.gaphor")

    assert selected_file.parts == (os.path.sep, "test", "path", "model.gaphor")


def test_save_dialog_with_full_file_name(file_chooser):
    selected_file = None

    def save_handler(f):
        nonlocal selected_file
        selected_file = f

    filename = Path("/test/path/model.gaphor")
    save_file_dialog(
        "title",
        save_handler,
        filename=filename,
        extension=".gaphor",
        filters=[],
    )

    assert file_chooser.stub_current_folder == str(filename.parent)
    assert file_chooser.stub_current_name == filename.name


def test_save_dialog_with_only_file_name(file_chooser):
    selected_file = None

    def save_handler(f):
        nonlocal selected_file
        selected_file = f

    filename = Path("model.gaphor")
    save_file_dialog(
        "title",
        save_handler,
        filename=filename,
        extension=".gaphor",
        filters=[],
    )

    # On GitHub CI, the path is returning the absolute path, both are fine
    assert file_chooser.stub_current_folder in (
        str(filename.parent),
        str(filename.parent.absolute()),
    )
    assert file_chooser.stub_current_name == filename.name


def test_save_dialog_filename_without_extension(file_chooser):
    selected_file = None

    def save_handler(f):
        nonlocal selected_file
        selected_file = f

    save_file_dialog(
        "title",
        save_handler,
        filename=None,
        extension=".gaphor",
        filters=[],
    )

    file_chooser.stub_select_file("/test/path", "model")

    assert selected_file.parts == (os.path.sep, "test", "path", "model.gaphor")
