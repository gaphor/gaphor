""" Tests for :module:`gaphor.misc.generic.event`."""

import unittest

from gaphor.misc.generic.event import Manager

__all__ = ("ManagerTests",)


class ManagerTests(unittest.TestCase):
    def makeHandler(self, effect):
        return lambda e: e.effects.append(effect)

    def createManager(self):

        return Manager()

    def test_subscribe_single_event(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), EventA)
        e = EventA()
        events.fire(e)
        self.assertEqual(len(e.effects), 1)
        self.assertTrue("handler1" in e.effects)

    def test_subscribe_via_decorator(self):
        events = self.createManager()
        events.subscriber(EventA)(self.makeHandler("handler1"))
        e = EventA()
        events.fire(e)
        self.assertEqual(len(e.effects), 1)
        self.assertTrue("handler1" in e.effects)

    def test_subscribe_event_inheritance(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), EventA)
        events.subscribe(self.makeHandler("handler2"), EventB)

        ea = EventA()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 1)
        self.assertTrue("handler1" in ea.effects)

        eb = EventB()
        events.fire(eb)
        self.assertEqual(len(eb.effects), 2)
        self.assertTrue("handler1" in eb.effects)
        self.assertTrue("handler2" in eb.effects)

    def test_subscribe_event_multiple_inheritance(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), EventA)
        events.subscribe(self.makeHandler("handler2"), EventC)
        events.subscribe(self.makeHandler("handler3"), EventD)

        ea = EventA()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 1)
        self.assertTrue("handler1" in ea.effects)

        ec = EventC()
        events.fire(ec)
        self.assertEqual(len(ec.effects), 1)
        self.assertTrue("handler2" in ec.effects)

        ed = EventD()
        events.fire(ed)
        self.assertEqual(len(ed.effects), 3)
        self.assertTrue("handler1" in ed.effects)
        self.assertTrue("handler2" in ed.effects)
        self.assertTrue("handler3" in ed.effects)

    def test_subscribe_no_events(self):
        events = self.createManager()

        ea = EventA()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 0)

    def test_subscribe_base_event(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), EventA)

        ea = EventB()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 1)
        self.assertTrue("handler1" in ea.effects)

    def test_subscribe_event_malformed_multiple_inheritance(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), EventA)
        events.subscribe(self.makeHandler("handler2"), EventD)
        events.subscribe(self.makeHandler("handler3"), EventE)

        ea = EventA()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 1)
        self.assertTrue("handler1" in ea.effects)

        ed = EventD()
        events.fire(ed)
        self.assertEqual(len(ed.effects), 2)
        self.assertTrue("handler1" in ed.effects)
        self.assertTrue("handler2" in ed.effects)

        ee = EventE()
        events.fire(ee)
        self.assertEqual(len(ee.effects), 3)
        self.assertTrue("handler1" in ee.effects)
        self.assertTrue("handler2" in ee.effects)
        self.assertTrue("handler3" in ee.effects)

    def test_subscribe_event_with_no_subscribers_in_the_middle_of_mro(self):
        events = self.createManager()
        events.subscribe(self.makeHandler("handler1"), Event)
        events.subscribe(self.makeHandler("handler2"), EventB)

        eb = EventB()
        events.fire(eb)
        self.assertEqual(len(eb.effects), 2)
        self.assertTrue("handler1" in eb.effects)
        self.assertTrue("handler2" in eb.effects)

    def test_unsubscribe_single_event(self):
        events = self.createManager()
        handler = self.makeHandler("handler1")
        events.subscribe(handler, EventA)
        events.unsubscribe(handler, EventA)
        e = EventA()
        events.fire(e)
        self.assertEqual(len(e.effects), 0)

    def test_unsubscribe_event_inheritance(self):
        events = self.createManager()
        handler1 = self.makeHandler("handler1")
        handler2 = self.makeHandler("handler2")
        events.subscribe(handler1, EventA)
        events.subscribe(handler2, EventB)
        events.unsubscribe(handler1, EventA)

        ea = EventA()
        events.fire(ea)
        self.assertEqual(len(ea.effects), 0)

        eb = EventB()
        events.fire(eb)
        self.assertEqual(len(eb.effects), 1)
        self.assertTrue("handler2" in eb.effects)


class Event:
    def __init__(self):
        self.effects = []


class EventA(Event):
    pass


class EventB(EventA):
    pass


class EventC(Event):
    pass


class EventD(EventA, EventC):
    pass


class EventE(EventD, EventA):
    pass
