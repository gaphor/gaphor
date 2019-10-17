import pytest
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
    recent_files = RecentFiles(event_manager, recent_manager)

    event_manager.handle(FileLoaded(None, "testfile.gaphor"))

    assert len(recent_manager.items) == 1
    assert recent_manager.items[0].startswith("file:///"), recent_manager.items[0]
