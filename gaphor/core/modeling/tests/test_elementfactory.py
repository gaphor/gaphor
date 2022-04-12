import gc
from collections.abc import Container, Iterable

import pytest

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
from gaphor.core.modeling.presentation import Presentation
from gaphor.UML import Operation, Parameter


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def test_element_factory_is_an_iterable(factory):
    assert isinstance(factory, Iterable)


def test_element_factory_is_a_container(factory):
    assert isinstance(factory, Container)


def test_create(factory):
    factory.create(Parameter)
    assert len(list(factory.values())) == 1


def test_create_is_idempotent(factory):
    param = factory.create(Parameter)
    new_param = factory.create_as(Parameter, param.id)
    assert param is new_param


def test_create_is_idempotent_but_validates_type(factory):
    param = factory.create(Parameter)
    with pytest.raises(TypeError):
        factory.create_as(Operation, param.id)


def test_should_not_create_presentation_elements(factory):
    with pytest.raises(TypeError):
        factory.create(Presentation)


def test_flush(factory):
    p = factory.create(Parameter)
    assert len(list(factory.values())) == 1
    factory.flush()
    del p

    gc.collect()

    assert not list(factory.values()), list(factory.values())


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

    assert not list(factory.values()), list(factory.values())

    p = factory.create(Parameter)
    p.defaultValue = "l"

    assert len(list(factory.values())) == 1

    p.unlink()
    del p

    assert not list(factory.values()), list(factory.values())


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
    yield ElementFactory(event_manager)
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
