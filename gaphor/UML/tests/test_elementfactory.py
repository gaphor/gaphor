
import unittest
from gaphor.UML import *
from gaphor.UML.interfaces import *
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
        assert len(ef.values()) == 1

    def testFlush(self):
        ef = self.factory

        p = ef.create(Parameter)
        #wp = weakref.ref(p)
        assert len(ef.values()) == 1
        ef.flush()
        del p

        gc.collect()

        #assert wp() is None
        assert len(ef.values()) == 0, ef.values()


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

        assert len(ef.values()) == 1

        p.unlink()

        assert len(ef.values()) == 0, ef.values()

        p = ef.create(Parameter)
        l = ef.create(LiteralString)
        p.defaultValue = l

        assert len(ef.values()) == 2

        p.unlink()
        del p

        assert len(ef.values()) == 0, ef.values()




from zope import component
from gaphor.application import Application

# Event handlers are registered as persisting top level handlers, since no
# unsubscribe functionality is provided.
handled = False
events = []
last_event = None

@component.adapter(IServiceEvent)
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
        p = ef.create(Parameter)
        self.assertTrue(IElementCreateEvent.providedBy(last_event) )
        self.assertTrue(handled)

    def testRemoveEvent(self):
        ef = self.factory
        global handled
        p = ef.create(Parameter)
        self.assertTrue(IElementCreateEvent.providedBy(last_event) )
        self.assertTrue(handled)
        self.clearEvents()
        p.unlink()
        self.assertTrue(IElementDeleteEvent.providedBy(last_event) )

    def testModelEvent(self):
        ef = self.factory
        global handled
        ef.notify_model()
        self.assertTrue(IModelFactoryEvent.providedBy(last_event) )

    def testFlushEvent(self):
        ef = self.factory
        global handled
        ef.flush()
        self.assertTrue(IFlushFactoryEvent.providedBy(last_event) )

    def test_deriveduntion_notify(self):
        from gaphor.UML.properties import association, derivedunion
        from gaphor.UML.element import Element
        
        class A(Element): pass
        class E(Element):
            notified=False
            def notify(self, name, pspec):
                if name == 'u':
                    self.notified = True

        E.a = association('a', A)
        E.u = derivedunion('u', A, 0, '*', E.a)

        e = self.factory.create(E)
        assert e.notified == False
        e.a = self.factory.create(A)
        assert e.notified == True



# vim:sw=4:et:ai
