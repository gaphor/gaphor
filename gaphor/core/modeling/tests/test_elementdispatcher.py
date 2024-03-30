# ruff: noqa: SLF001
import pytest

from gaphor import UML
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Element, ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher, EventWatcher
from gaphor.core.modeling.properties import association
from gaphor.UML.modelinglanguage import UMLModelingLanguage


class Event:
    def __init__(self):
        self.events = []

    def handler(self, event):
        self.events.append(event)


class A(Element):
    one: association
    two: association

    def __init__(self, id=None, model=None):
        super().__init__(id, model)


A.one = association("one", A, lower=0, upper=1, composite=True)
A.two = association("two", A, lower=0, upper=2, composite=True)


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def modeling_language():
    return UMLModelingLanguage()


@pytest.fixture
def dispatcher(event_manager, modeling_language):
    return ElementDispatcher(event_manager, modeling_language)


@pytest.fixture
def element_factory(event_manager, dispatcher):
    return ElementFactory(event_manager, dispatcher)


@pytest.fixture
def uml_class(element_factory):
    return element_factory.create(UML.Class)


@pytest.fixture
def uml_parameter(element_factory):
    return element_factory.create(UML.Parameter)


@pytest.fixture
def uml_operation(element_factory):
    return element_factory.create(UML.Operation)


@pytest.fixture
def uml_transition(element_factory):
    return element_factory.create(UML.Transition)


@pytest.fixture
def uml_constraint(element_factory):
    return element_factory.create(UML.Constraint)


@pytest.fixture
def event():
    return Event()


@pytest.fixture
def handler():
    events = []

    def handler(event):
        events.append(event)

    handler.events = events
    return handler


def test_register_handler(dispatcher, uml_class, uml_parameter, uml_operation, event):
    element = uml_class
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert len(dispatcher._handlers) == 1
    assert list(dispatcher._handlers.keys())[0] == (element, UML.Class.ownedOperation)

    # Add some properties:

    # 1:
    element.ownedOperation = uml_operation
    # 2:
    p = element.ownedOperation[0].ownedParameter = uml_parameter
    # 3:
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert len(event.events) == 3
    assert len(dispatcher._handlers) == 3


def test_register_handler_twice(
    dispatcher, uml_class, uml_operation, uml_parameter, event
):
    """Multiple registrations have no effect."""
    # Add some properties:
    element = uml_class
    element.ownedOperation = uml_operation
    p = element.ownedOperation[0].ownedParameter = uml_parameter
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")

    n_handlers = len(dispatcher._handlers)

    assert len(event.events) == 0
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert n_handlers == len(dispatcher._handlers)
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert n_handlers == len(dispatcher._handlers)
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert n_handlers == len(dispatcher._handlers)

    p.name = "func"
    assert len(event.events) == 1


def test_unregister_handler(dispatcher, uml_class, uml_operation, uml_parameter, event):
    # First some setup:
    element = uml_class
    o = element.ownedOperation = uml_operation
    p = element.ownedOperation[0].ownedParameter = uml_parameter
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert len(dispatcher._handlers) == 3
    assert dispatcher._handlers[element, UML.Class.ownedOperation]
    assert dispatcher._handlers[o, UML.Operation.ownedParameter]
    assert dispatcher._handlers[p, UML.Parameter.name]

    dispatcher.unsubscribe(event.handler)

    assert len(dispatcher._handlers) == 0, dispatcher._handlers
    assert len(dispatcher._reverse) == 0, dispatcher._reverse
    # Should not fail here too:
    dispatcher.unsubscribe(event.handler)


def test_notification(
    dispatcher, uml_class, uml_operation, uml_parameter, event, element_factory
):
    """Test notifications with Class object."""
    element = uml_class
    o = element.ownedOperation = uml_operation
    p = element.ownedOperation[0].ownedParameter = uml_parameter
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.ownedParameter.name")
    assert len(dispatcher._handlers) == 3
    assert not event.events

    element.ownedOperation = element_factory.create(UML.Operation)
    assert len(event.events) == 1, event.events
    assert len(dispatcher._handlers) == 4

    p.name = "othername"
    assert len(event.events) == 2, event.events

    del element.ownedOperation[o]
    assert len(dispatcher._handlers) == 2


def test_notification_2(
    dispatcher, uml_transition, uml_constraint, event, element_factory
):
    """Test notifications with Transition object."""
    element = uml_transition
    g = element.guard = uml_constraint
    dispatcher.subscribe(event.handler, element, "guard.specification")
    assert len(dispatcher._handlers) == 2
    assert not event.events
    assert (element.guard, UML.Constraint.specification) in list(
        dispatcher._handlers.keys()
    ), list(dispatcher._handlers.keys())

    g.specification = "x"
    assert len(event.events) == 1, event.events

    element.guard = element_factory.create(UML.Constraint)
    assert len(event.events) == 2, event.events
    assert len(dispatcher._handlers) == 2, len(dispatcher._handlers)
    assert (element.guard, UML.Constraint.specification) in list(
        dispatcher._handlers.keys()
    )


def test_notification_of_change(
    dispatcher, uml_transition, uml_constraint, event, element_factory
):
    """Test notifications with Transition object."""
    element = uml_transition
    g = element.guard = uml_constraint
    dispatcher.subscribe(event.handler, element, "guard.specification")
    assert len(dispatcher._handlers) == 2
    assert not event.events

    g.specification = "x"
    assert len(event.events) == 1, event.events

    element.guard = element_factory.create(UML.Constraint)
    assert len(event.events) == 2, event.events


def test_notification_with_composition(
    dispatcher, uml_class, uml_operation, uml_constraint, event
):
    """Test unregister with composition.

    Use Class.ownedOperation.precondition.
    """
    element = uml_class
    o = element.ownedOperation = uml_operation
    p = element.ownedOperation[0].precondition = uml_constraint
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.precondition.name")
    assert len(dispatcher._handlers) == 3
    assert not event.events

    del element.ownedOperation[o]
    assert len(dispatcher._handlers) == 1


def test_notification_with_incompatible_elements(
    dispatcher, uml_transition, uml_constraint, event
):
    """Test unregister with composition.

    Use Class.ownedOperation.precondition.
    """
    element = uml_transition
    g = element.guard = uml_constraint
    dispatcher.subscribe(event.handler, element, "guard.specification")
    assert len(dispatcher._handlers) == 2
    assert not event.events
    assert (element.guard, UML.Constraint.specification) in list(
        dispatcher._handlers.keys()
    ), list(dispatcher._handlers.keys())

    g.specification = "x"
    assert len(event.events) == 1, event.events

    g.specification = "a"
    assert len(event.events) == 2, event.events


def test_notification_with_class(element_factory, dispatcher, handler):
    """Test notifications with Class object."""
    element = element_factory.create(UML.Class)
    o = element.ownedOperation = element_factory.create(UML.Operation)
    p = element.ownedOperation[0].ownedParameter = element_factory.create(UML.Parameter)
    p.name = "func"
    dispatcher.subscribe(handler, element, "ownedOperation.ownedParameter.name")
    assert len(dispatcher._handlers) == 3
    assert not handler.events

    element.ownedOperation = element_factory.create(UML.Operation)
    assert len(handler.events) == 1, handler.events
    assert len(dispatcher._handlers) == 4

    p.name = "othername"
    assert len(handler.events) == 2, handler.events

    del element.ownedOperation[o]
    assert len(dispatcher._handlers) == 2


def test_association_notification(element_factory, dispatcher, handler):
    """Test notifications with Class object.

    Tricky case where no events are fired.
    """
    element = element_factory.create(UML.Association)
    p1 = element.memberEnd = element_factory.create(UML.Property)
    element.memberEnd = element_factory.create(UML.Property)

    assert len(element.memberEnd) == 2
    dispatcher.subscribe(handler, element, "memberEnd.name")
    assert len(dispatcher._handlers) == 3, len(dispatcher._handlers)
    assert not handler.events

    p1.name = "foo"
    assert len(handler.events) == 1, (handler.events, dispatcher._handlers)
    assert len(dispatcher._handlers) == 3

    p1.name = "othername"
    assert len(handler.events) == 2, handler.events

    p1.name = "othername"
    assert len(handler.events) == 2, handler.events


def test_association_notification_complex(element_factory, dispatcher, handler):
    """Test notifications with Class object.

    Tricky case where no events are fired.
    """
    element = element_factory.create(UML.Association)
    p1 = element.memberEnd = element_factory.create(UML.Property)
    p2 = element.memberEnd = element_factory.create(UML.Property)
    p1.lowerValue = "0"
    p1.upperValue = "1"
    p2.lowerValue = "1"
    p2.upperValue = "*"

    assert len(element.memberEnd) == 2

    base = "memberEnd[Property]."
    dispatcher.subscribe(handler, element, f"{base}name")
    dispatcher.subscribe(handler, element, f"{base}aggregation")
    dispatcher.subscribe(handler, element, f"{base}classifier")
    dispatcher.subscribe(handler, element, f"{base}lowerValue")
    dispatcher.subscribe(handler, element, f"{base}upperValue")

    assert len(dispatcher._handlers) == 11, len(dispatcher._handlers)
    assert not handler.events

    p1.name = "foo"
    assert len(handler.events) == 1, (handler.events, dispatcher._handlers)
    assert len(dispatcher._handlers) == 11

    p1.name = "othername"
    assert len(handler.events) == 2, handler.events


def test_diamond(element_factory, dispatcher, handler):
    """Test diamond shaped dependencies a -> b -> c, a -> b' -> c."""
    a = element_factory.create(A)
    watcher = EventWatcher(a, dispatcher, handler)
    watcher.watch("one.two.one.two")

    a.one = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two[0].one = element_factory.create(A)
    a.one.two[1].one = a.one.two[0].one
    a.one.two[0].one.two = element_factory.create(A)

    assert len(handler.events) == 6

    a.unlink()
    watcher.unsubscribe_all()
    watcher.unsubscribe_all()


def test_big_diamond(element_factory, dispatcher, handler):
    """Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' ->
    d."""
    a = element_factory.create(A)
    watcher = EventWatcher(a, dispatcher, handler)
    watcher.watch("one.two.one.two")

    a.one = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two[0].one = element_factory.create(A)
    a.one.two[1].one = element_factory.create(A)
    a.one.two[0].one.two = element_factory.create(A)
    a.one.two[1].one.two = a.one.two[0].one.two[0]

    assert len(handler.events) == 7

    a.unlink()
    watcher.unsubscribe_all()
    watcher.unsubscribe_all()
    assert len(dispatcher._handlers) == 0


def test_braking_big_diamond(element_factory, dispatcher, handler):
    """Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' ->
    d."""
    a = element_factory.create(A)
    watcher = EventWatcher(a, dispatcher, handler)
    watcher.watch("one.two.one.two")

    a.one = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two[0].one = element_factory.create(A)
    a.one.two[1].one = element_factory.create(A)
    a.one.two[0].one.two = element_factory.create(A)
    a.one.two[1].one.two = a.one.two[0].one.two[0]

    assert len(handler.events) == 7
    assert len(dispatcher._handlers) == 6

    del a.one.two[0].one
    watcher.unsubscribe_all()
    watcher.unsubscribe_all()
    assert len(dispatcher._handlers) == 0


def test_cyclic(element_factory, dispatcher, handler):
    """Test cyclic dependency a -> b -> c -> a."""
    a = element_factory.create(A)
    watcher = EventWatcher(a, dispatcher, handler)
    watcher.watch("one.two.one.two")

    a.one = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two = element_factory.create(A)
    a.one.two[0].one = a

    assert 4 == len(handler.events)

    a.unlink()
    assert 1 == len(dispatcher._handlers)
