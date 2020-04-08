import gc

import pytest

from gaphor.application import Session
from gaphor.core import event_handler
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.event import (
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
    ServiceEvent,
)
from gaphor.UML import Parameter


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def test_create(factory):
    factory.create(Parameter)
    assert len(list(factory.values())) == 1


def test_flush(factory):
    p = factory.create(Parameter)
    assert len(list(factory.values())) == 1
    factory.flush()
    del p

    gc.collect()

    assert len(list(factory.values())) == 0, list(factory.values())


def test_without_application(factory):
    factory.create(Parameter)
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


def clear_events():
    global handled, events, last_event
    handled = False
    events = []
    last_event = None


@pytest.fixture
def element_factory():
    event_manager = EventManager()
    event_manager.subscribe(handler)
    clear_events()
    factory = ElementFactory(event_manager)
    yield factory
    clear_events()


def test_create_event(element_factory):
    element_factory.create(Parameter)
    assert isinstance(last_event, ElementCreated)
    assert handled


def test_remove_event(element_factory):
    p = element_factory.create(Parameter)
    clear_events()
    p.unlink()
    assert isinstance(last_event, ElementDeleted)


def test_model_event(element_factory):
    element_factory.model_ready()
    assert isinstance(last_event, ModelReady)


def test_flush_event(element_factory):
    element_factory.create(Parameter)
    del events[:]
    element_factory.flush()
    assert len(events) == 1, events
    assert isinstance(last_event, ModelFlushed)


def test_no_create_events_when_blocked(element_factory):
    with element_factory.block_events():
        element_factory.create(Parameter)
    assert events == [], events
