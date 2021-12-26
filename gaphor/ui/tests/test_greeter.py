from gaphor.diagram.tests.fixtures import find
from gaphor.ui import APPLICATION_ID
from gaphor.ui.greeter import Greeter


class RecentManagerStub:
    def __init__(self, *items):
        self.items = items

    def get_items(self):
        return self.items


class RecentInfoStub:
    def __init__(self, uri):
        self.uri = uri

    def get_applications(self):
        return APPLICATION_ID

    def exists(self):
        return True

    def get_uri(self):
        return self.uri

    def get_uri_display(self):
        return self.uri


def test_greeter_with_recent_files(event_manager):
    recent_manager = RecentManagerStub(RecentInfoStub("file://path/to/foo.gaphor"))
    greeter = Greeter(None, event_manager, recent_manager)

    greeter.recent_files()
    widget = greeter.greeter
    stack = find(widget, "stack")

    assert stack.get_visible_child_name() == "recent-files"


def test_greeter_with_no_recent_files(event_manager):
    recent_manager = RecentManagerStub()
    greeter = Greeter(None, event_manager, recent_manager)

    greeter.recent_files()
    widget = greeter.greeter
    stack = find(widget, "stack")

    assert stack.get_visible_child_name() == "new-model"
