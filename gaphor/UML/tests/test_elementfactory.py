
from __future__ import absolute_import
import unittest
from gaphor.UML import interfaces
from gaphor.UML import elementfactory
from gaphor.UML import uml2
import gc


class ElementFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = elementfactory.ElementFactory()

    def tearDown(self):
        del self.factory

    def testCreate(self):
        ef = self.factory

        p = ef.create(uml2.Parameter)
        assert len(list(ef.values())) == 1

    def testFlush(self):
        ef = self.factory

        p = ef.create(uml2.Parameter)
        #wp = weakref.ref(p)
        assert len(list(ef.values())) == 1
        ef.flush()
        del p

        gc.collect()

        #assert wp() is None
        assert len(list(ef.values())) == 0, list(ef.values())


    def testWithoutApplication(self):
        ef = elementfactory.ElementFactory()

        p = ef.create(uml2.Parameter)
        assert ef.size() == 1, ef.size()

        ef.flush()
        assert ef.size() == 0, ef.size()

        p = ef.create(uml2.Parameter)
        assert ef.size() == 1, ef.size()

        p.unlink()
        assert ef.size() == 0, ef.size()


    def testUnlink(self):
        ef = self.factory
        p = ef.create(uml2.Parameter)

        assert len(list(ef.values())) == 1

        p.unlink()

        assert len(list(ef.values())) == 0, list(ef.values())

        p = ef.create(uml2.Parameter)
        p.defaultValue = 'l'

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

@component.adapter(interfaces.IServiceEvent)
def handler(event):
    global handled, events, last_event
    handled = True
    events.append(event)
    last_event = event

component.provideHandler(handler)


class ElementFactoryServiceTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(['element_factory'])
        self.factory = Application.get_service('element_factory')

    def tearDown(self):
        del self.factory
        self.clearEvents()
        Application.shutdown()

    def clearEvents(self):
        global handled, events, last_event
        handled = False
        events = [ ]
        last_event = None

    def testCreateEvent(self):
        ef = self.factory
        global handled
        p = ef.create(uml2.Parameter)
        self.assertTrue(interfaces.IElementCreateEvent.providedBy(last_event) )
        self.assertTrue(handled)

    def testRemoveEvent(self):
        ef = self.factory
        global handled
        p = ef.create(uml2.Parameter)
        self.assertTrue(interfaces.IElementCreateEvent.providedBy(last_event) )
        self.assertTrue(handled)
        self.clearEvents()
        p.unlink()
        self.assertTrue(interfaces.IElementDeleteEvent.providedBy(last_event) )

    def testModelEvent(self):
        ef = self.factory
        global handled
        ef.notify_model()
        self.assertTrue(interfaces.IModelFactoryEvent.providedBy(last_event) )

    def testFlushEvent(self):
        ef = self.factory
        global handled
        ef.flush()
        self.assertTrue(interfaces.IFlushFactoryEvent.providedBy(last_event) )


# vim:sw=4:et:ai
