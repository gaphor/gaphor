import pathlib

import pytest
from gi.repository import GLib

from gaphor.services.eventmanager import EventManager
from gaphor.ui.event import FileLoaded
from gaphor.ui.recentfiles import RecentFiles


class RecentManagerStub:
    def __init__(self):
        self.items = []

    def add_full(self, uri, meta):
        self.items.append(uri)


@pytest.fixture
def event_manager():
    return EventManager()


def test_add_new_recent_file(event_manager):
    recent_manager = RecentManagerStub()
    RecentFiles(event_manager, recent_manager)

    event_manager.handle(FileLoaded(None, "testfile.gaphor"))

    assert len(recent_manager.items) == 1
    assert recent_manager.items[0].startswith("file:///"), recent_manager.items[0]


def test_uri_conversion_with_spaces():
    filename = "/path name/with spaces"
    uri = GLib.filename_to_uri(filename)
    decoded_filename, hostname = GLib.filename_from_uri(uri)
    decoded_posix_filename = pathlib.PurePath(decoded_filename).as_posix()

    assert uri == "file:///path%20name/with%20spaces"
    assert decoded_posix_filename == filename
    assert hostname is None


def test_decode_not_encoded_uri():
    filename = "/path name/with spaces"
    uri = f"file://{filename}"
    decoded_filename, hostname = GLib.filename_from_uri(uri)
    decoded_posix_filename = pathlib.PurePath(decoded_filename).as_posix()

    assert decoded_posix_filename == filename
    assert hostname is None
