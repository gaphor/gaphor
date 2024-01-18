import pytest

from gaphor.core.eventmanager import event_handler


class Event:
    pass


class OtherEvent:
    pass


@event_handler(Event)
class Subscriber:
    def __init__(self, exception=None):
        self.events = []
        self.exception = exception

    def __call__(self, event):
        self.events.append(event)
        if self.exception:
            raise self.exception()


def create_handler(event_type):
    events = []

    @event_handler(event_type)
    def handler(event):
        events.append(event)

    return handler, events


@pytest.fixture
def subscriber(event_manager):
    s = Subscriber()
    event_manager.subscribe(s)
    return s


def test_event_manager(event_manager, subscriber):
    event = Event()

    event_manager.handle(event)

    assert event in subscriber.events


def test_error_in_handler(event_manager):
    event = Event()
    error = Subscriber(ValueError)
    after = Subscriber()

    event_manager.subscribe(error)
    event_manager.subscribe(after)

    with pytest.raises(ExceptionGroup):
        event_manager.handle(event)

    assert event in error.events
    assert event in after.events


def test_error_in_handler_and_second_event(event_manager):
    @event_handler(Event)
    def error_handler(event):
        event_manager.handle(OtherEvent())
        raise ValueError()

    other_handler, other_events = create_handler(OtherEvent)

    event_manager.subscribe(error_handler)
    event_manager.subscribe(other_handler)

    event = Event()

    with pytest.raises(ExceptionGroup):
        event_manager.handle(event)

    assert not other_events


def test_priority_handler_error_in_handler_and_second_event(event_manager):
    @event_handler(Event)
    def error_handler(event):
        event_manager.handle(OtherEvent())
        raise ValueError()

    other_handler, other_events = create_handler(OtherEvent)

    event_manager.subscribe(error_handler)
    event_manager.priority_subscribe(other_handler)

    event = Event()

    with pytest.raises(ExceptionGroup):
        event_manager.handle(event)

    assert other_events
