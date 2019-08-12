""" Tests for :module:`gaphor.misc.generic.event`."""

from typing import List
from gaphor.misc.generic.event import Manager


def make_handler(effect):
    return lambda e: e.effects.append(effect)


def create_manager():
    return Manager()


def test_subscribe_single_event():
    events = create_manager()
    events.subscribe(make_handler("handler1"), EventA)
    e = EventA()
    events.handle(e)
    assert len(e.effects) == 1
    assert "handler1" in e.effects


def test_subscribe_via_decorator():
    events = create_manager()
    events.subscriber(EventA)(make_handler("handler1"))
    e = EventA()
    events.handle(e)
    assert len(e.effects) == 1
    assert "handler1" in e.effects


def test_subscribe_event_inheritance():
    events = create_manager()
    events.subscribe(make_handler("handler1"), EventA)
    events.subscribe(make_handler("handler2"), EventB)

    ea = EventA()
    events.handle(ea)
    assert len(ea.effects) == 1
    assert "handler1" in ea.effects

    eb = EventB()
    events.handle(eb)
    assert len(eb.effects) == 2
    assert "handler1" in eb.effects
    assert "handler2" in eb.effects


def test_subscribe_event_multiple_inheritance():
    events = create_manager()
    events.subscribe(make_handler("handler1"), EventA)
    events.subscribe(make_handler("handler2"), EventC)
    events.subscribe(make_handler("handler3"), EventD)

    ea = EventA()
    events.handle(ea)
    assert len(ea.effects) == 1
    assert "handler1" in ea.effects

    ec = EventC()
    events.handle(ec)
    assert len(ec.effects) == 1
    assert "handler2" in ec.effects

    ed = EventD()
    events.handle(ed)
    assert len(ed.effects) == 3
    assert "handler1" in ed.effects
    assert "handler2" in ed.effects
    assert "handler3" in ed.effects


def test_subscribe_no_events():
    events = create_manager()

    ea = EventA()
    events.handle(ea)
    assert len(ea.effects) == 0


def test_subscribe_base_event():
    events = create_manager()
    events.subscribe(make_handler("handler1"), EventA)

    ea = EventB()
    events.handle(ea)
    assert len(ea.effects) == 1
    assert "handler1" in ea.effects


def test_subscribe_event_malformed_multiple_inheritance():
    events = create_manager()
    events.subscribe(make_handler("handler1"), EventA)
    events.subscribe(make_handler("handler2"), EventD)
    events.subscribe(make_handler("handler3"), EventE)

    ea = EventA()
    events.handle(ea)
    assert len(ea.effects) == 1
    assert "handler1" in ea.effects

    ed = EventD()
    events.handle(ed)
    assert len(ed.effects) == 2
    assert "handler1" in ed.effects
    assert "handler2" in ed.effects

    ee = EventE()
    events.handle(ee)
    assert len(ee.effects) == 3
    assert "handler1" in ee.effects
    assert "handler2" in ee.effects
    assert "handler3" in ee.effects


def test_subscribe_event_with_no_subscribers_in_the_middle_of_mro():
    events = create_manager()
    events.subscribe(make_handler("handler1"), Event)
    events.subscribe(make_handler("handler2"), EventB)

    eb = EventB()
    events.handle(eb)
    assert len(eb.effects) == 2
    assert "handler1" in eb.effects
    assert "handler2" in eb.effects


def test_unsubscribe_single_event():
    events = create_manager()
    handler = make_handler("handler1")
    events.subscribe(handler, EventA)
    events.unsubscribe(handler, EventA)
    e = EventA()
    events.handle(e)
    assert len(e.effects) == 0


def test_unsubscribe_event_inheritance():
    events = create_manager()
    handler1 = make_handler("handler1")
    handler2 = make_handler("handler2")
    events.subscribe(handler1, EventA)
    events.subscribe(handler2, EventB)
    events.unsubscribe(handler1, EventA)

    ea = EventA()
    events.handle(ea)
    assert len(ea.effects) == 0

    eb = EventB()
    events.handle(eb)
    assert len(eb.effects) == 1
    assert "handler2" in eb.effects


class Event:
    def __init__(self):
        self.effects: List[object] = []


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
