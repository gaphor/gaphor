import unittest
from gaphor.event import ServiceEvent
from gaphor.UML import *
from gaphor.UML.event import *
import gc
import weakref, sys


class ElementFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = ElementFactory()

    def tearDown(self):
        del self.factory

    def testCreate(self):
        ef = self.factory

        p = ef.create(Parameter)
        assert len(list(ef.values())) == 1

    def testFlush(self):
        ef = self.factory

        p = ef.create(Parameter)
        # wp = weakref.ref(p)
        assert len(list(ef.values())) == 1
        ef.flush()
        del p

        gc.collect()

        # assert wp() is None
        assert len(list(ef.values())) == 0, list(ef.values())

    def testWithoutApplication(self):
        ef = ElementFactory()

        p = ef.create(Parameter)
        assert ef.size() == 1, ef.size()

        ef.flush()
        assert ef.size() == 0, ef.size()

        p = ef.create(Parameter)
        assert ef.size() == 1, ef.size()

        p.unlink()
        assert ef.size() == 0, ef.size()

    def testUnlink(self):
        ef = self.factory
        p = ef.create(Parameter)

        assert len(list(ef.values())) == 1

        p.unlink()

        assert len(list(ef.values())) == 0, list(ef.values())

        p = ef.create(Parameter)
        p.defaultValue = "l"

        assert len(list(ef.values())) == 1

        p.unlink()
        del p

        assert len(list(ef.values())) == 0, list(ef.values())


from zope import component
from gaphor.application import Application

# Event handlers are registered as persisting top level handlers, since no
# unsubscribe functionality is provided.
handled = False
events = []
last_event = None


@component.adapter(ServiceEvent)
def handler(event):
    global handled, events, last_event
    handled = True
    events.append(event)
    last_event = event


component.provideHandler(handler)


def clearEvents():
    global handled, events, last_event
    handled = False
    events = []
    last_event = None


class ElementFactoryServiceTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(["element_factory"])
        self.factory = Application.get_service("element_factory")
        clearEvents()

    def tearDown(self):
        del self.factory
        clearEvents()
        Application.shutdown()

    def testCreateEvent(self):
        ef = self.factory
        p = ef.create(Parameter)

        assert isinstance(last_event, ElementCreateEvent)
        assert handled

    def testRemoveEvent(self):
        ef = self.factory
        p = ef.create(Parameter)
        clearEvents()
        p.unlink()

        assert isinstance(last_event, ElementDeleteEvent)

    def testModelEvent(self):
        ef = self.factory
        ef.notify_model()

        assert isinstance(last_event, ModelFactoryEvent)

    def testFlushEvent(self):
        ef = self.factory
        ef.create(Parameter)
        del events[:]

        ef.flush()

        assert len(events) == 1, events
        assert isinstance(last_event, FlushFactoryEvent)

    def test_no_create_events_when_blocked(self):
        ef = self.factory
        with ef.block_events():
            ef.create(Parameter)

        assert events == [], events
