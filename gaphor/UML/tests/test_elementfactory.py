import pytest
import unittest
from gaphor.event import ServiceEvent
from gaphor.services.eventmanager import EventManager
from gaphor.UML import *
from gaphor.UML.event import *
import gc
import weakref, sys


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def test_create(factory):
    p = factory.create(Parameter)
    assert len(list(factory.values())) == 1


def testFlush(factory):
    p = factory.create(Parameter)
    # wp = weakref.ref(p)
    assert len(list(factory.values())) == 1
    factory.flush()
    del p

    gc.collect()

    # assert wp() is None
    assert len(list(factory.values())) == 0, list(factory.values())


def test_without_application(factory):
    p = factory.create(Parameter)
    assert factory.size() == 1, factory.size()

    factory.flush()
    assert factory.size() == 0, factory.size()

    p = factory.create(Parameter)
    assert factory.size() == 1, factory.size()

    p.unlink()
    assert factory.size() == 0, factory.size()


def test_unlink(factory):
    p = factory.create(Parameter)

    assert len(list(factory.values())) == 1

    p.unlink()

    assert len(list(factory.values())) == 0, list(factory.values())

    p = factory.create(Parameter)
    p.defaultValue = "l"

    assert len(list(factory.values())) == 1

    p.unlink()
    del p

    assert len(list(factory.values())) == 0, list(factory.values())


from gaphor.application import Application
from gaphor.core import event_handler

# Event handlers are registered as persisting top level handlers, since no
# unsubscribe functionality is provided.
handled = False
events = []
last_event = None


@event_handler(ServiceEvent)
def handler(event):
    global handled, events, last_event
    handled = True
    events.append(event)
    last_event = event


def clearEvents():
    global handled, events, last_event
    handled = False
    events = []
    last_event = None


class ElementFactoryServiceTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(["event_manager", "component_registry", "element_factory"])
        self.factory = Application.get_service("element_factory")
        event_manager = Application.get_service("event_manager")
        event_manager.subscribe(handler)
        clearEvents()

    def tearDown(self):
        del self.factory
        clearEvents()
        Application.shutdown()

    def testCreateEvent(self):
        factory = self.factory
        p = factory.create(Parameter)

        assert isinstance(last_event, ElementCreateEvent)
        assert handled

    def testRemoveEvent(self):
        factory = self.factory
        p = factory.create(Parameter)
        clearEvents()
        p.unlink()

        assert isinstance(last_event, ElementDeleteEvent)

    def testModelEvent(self):
        factory = self.factory
        factory.notify_model()

        assert isinstance(last_event, ModelFactoryEvent)

    def testFlushEvent(self):
        factory = self.factory
        factory.create(Parameter)
        del events[:]

        factory.flush()

        assert len(events) == 1, events
        assert isinstance(last_event, FlushFactoryEvent)

    def test_no_create_events_when_blocked(self):
        factory = self.factory
        with factory.block_events():
            factory.create(Parameter)

        assert events == [], events
