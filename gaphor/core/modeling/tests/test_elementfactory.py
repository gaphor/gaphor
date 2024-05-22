import gc
from collections.abc import Container, Iterable

import pytest

from gaphor.core import event_handler
from gaphor.core.modeling.event import (
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ServiceEvent,
)
from gaphor.core.modeling.presentation import Presentation
from gaphor.UML import Operation, Parameter


def test_element_factory_is_an_iterable(element_factory):
    assert isinstance(element_factory, Iterable)


def test_element_factory_is_a_container(element_factory):
    assert isinstance(element_factory, Container)


def test_create(element_factory):
    element_factory.create(Parameter)
    assert len(list(element_factory.values())) == 1


def test_create_is_idempotent(element_factory):
    param = element_factory.create(Parameter)
    new_param = element_factory.create_as(Parameter, param.id)
    assert param is new_param


def test_create_is_idempotent_but_validates_type(element_factory):
    param = element_factory.create(Parameter)
    with pytest.raises(TypeError):
        element_factory.create_as(Operation, param.id)


def test_should_not_create_presentation_elements(element_factory):
    with pytest.raises(TypeError):
        element_factory.create(Presentation)


def test_flush(element_factory):
    p = element_factory.create(Parameter)
    assert len(list(element_factory.values())) == 1
    element_factory.flush()
    del p

    gc.collect()

    assert not list(element_factory.values()), list(element_factory.values())


def test_without_application(element_factory):
    element_factory.create(Parameter)
    assert element_factory.size() == 1, element_factory.size()

    element_factory.flush()
    assert element_factory.size() == 0, element_factory.size()

    p = element_factory.create(Parameter)
    assert element_factory.size() == 1, element_factory.size()

    p.unlink()
    assert element_factory.size() == 0, element_factory.size()


def test_unlink(element_factory):
    p = element_factory.create(Parameter)

    assert len(list(element_factory.values())) == 1

    p.unlink()

    assert not list(element_factory.values()), list(element_factory.values())

    p = element_factory.create(Parameter)
    p.defaultValue = "l"

    assert len(list(element_factory.values())) == 1

    p.unlink()
    del p

    assert not list(element_factory.values()), list(element_factory.values())


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


@pytest.fixture(autouse=True)
def subscribe_handlers(event_manager):
    event_manager.subscribe(handler)
    clear_events()
    yield None
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


class TriggerUnlink:
    def __init__(self, element):
        self.element = element


class CheckModel:
    def __init__(self, element):
        self.element = element


def test_indirect_delete_of_element(event_manager, element_factory):
    @event_handler(CheckModel)
    def on_check_model(event):
        assert event.element.model
        assert event.element in element_factory

    @event_handler(TriggerUnlink)
    def on_trigger_unlink(event):
        event_manager.handle(CheckModel(event.element))
        event.element.unlink()

    event_manager.subscribe(on_check_model)
    event_manager.subscribe(on_trigger_unlink)

    operation = element_factory.create(Operation)
    event_manager.handle(TriggerUnlink(operation))

    with pytest.raises(TypeError):
        assert operation.model
    assert operation not in element_factory
