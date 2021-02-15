import pytest

from gaphor.services.properties import FileBackend, Properties, get_config_dir


class MockEventManager(list):
    def handle(self, event):
        self.append(event)


@pytest.fixture
def prop(tmpdir):
    backend = FileBackend(tmpdir)
    events = MockEventManager()
    properties = Properties(events, backend)

    yield properties
    properties.shutdown()


def test_properties(prop):
    prop.set("test1", 2)
    assert len(prop.event_manager) == 1, prop.event_manager
    event = prop.event_manager[0]
    assert "test1" == event.key
    assert None is event.old_value
    assert event.new_value == 2
    assert prop("test1") == 2

    prop.set("test1", 2)
    assert len(prop.event_manager) == 1

    prop.set("test1", "foo")
    assert len(prop.event_manager) == 2
    event = prop.event_manager[1]
    assert "test1" == event.key
    assert event.old_value == 2
    assert "foo" == event.new_value
    assert "foo" == prop("test1")

    assert prop("test2", 3) == 3
    assert prop("test2", 4) == 3


def test_config_dir():
    config_dir = get_config_dir()
    assert config_dir.endswith("gaphor")
