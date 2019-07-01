import pytest

from gaphor import UML
from gaphor.UML import Element
from gaphor.UML.elementdispatcher import ElementDispatcher
from gaphor.UML.elementdispatcher import EventWatcher
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.properties import association
from gaphor.services.eventmanager import EventManager
from gaphor.tests import TestCase


class Event:
    def __init__(self):
        self.events = []

    def handler(self, event):
        self.events.append(event)


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def dispatcher(event_manager):
    element_dispatcher = ElementDispatcher(event_manager)
    yield element_dispatcher
    element_dispatcher.shutdown()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


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


def test_register_handler(dispatcher, uml_class, uml_parameter, uml_operation, event):
    element = uml_class
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert len(dispatcher._handlers) == 1
    assert list(dispatcher._handlers.keys())[0] == (element, UML.Class.ownedOperation)

    # Add some properties:

    # 1:
    element.ownedOperation = uml_operation
    # 2:
    p = element.ownedOperation[0].formalParameter = uml_parameter
    # 3:
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert len(event.events) == 3
    assert len(dispatcher._handlers) == 3


def test_register_handler_twice(
    dispatcher, uml_class, uml_operation, uml_parameter, event
):
    """
    Multiple registrations have no effect.
    """
    # Add some properties:
    element = uml_class
    element.ownedOperation = uml_operation
    p = element.ownedOperation[0].formalParameter = uml_parameter
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")

    n_handlers = len(dispatcher._handlers)

    assert 0 == len(event.events)
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert n_handlers == len(dispatcher._handlers)
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert n_handlers == len(dispatcher._handlers)
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert n_handlers == len(dispatcher._handlers)

    p.name = "func"
    assert len(event.events) == 1


def test_unregister_handler(dispatcher, uml_class, uml_operation, uml_parameter, event):
    # First some setup:
    element = uml_class
    o = element.ownedOperation = uml_operation
    p = element.ownedOperation[0].formalParameter = uml_parameter
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
    assert len(dispatcher._handlers) == 3
    assert dispatcher._handlers[element, UML.Class.ownedOperation]
    assert dispatcher._handlers[o, UML.Operation.parameter]
    assert dispatcher._handlers[p, UML.Parameter.name]

    dispatcher.unsubscribe(event.handler)

    assert len(dispatcher._handlers) == 0, dispatcher._handlers
    assert len(dispatcher._reverse) == 0, dispatcher._reverse
    # Should not fail here too:
    dispatcher.unsubscribe(event.handler)


def test_notification(
    dispatcher, uml_class, uml_operation, uml_parameter, event, element_factory
):
    """
    Test notifications with Class object.
    """
    element = uml_class
    o = element.ownedOperation = uml_operation
    p = element.ownedOperation[0].formalParameter = uml_parameter
    p.name = "func"
    dispatcher.subscribe(event.handler, element, "ownedOperation.parameter.name")
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
    """
    Test notifications with Transition object.
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

    element.guard = element_factory.create(UML.Constraint)
    assert len(event.events) == 2, event.events
    assert len(dispatcher._handlers) == 2, len(dispatcher._handlers)
    assert (element.guard, UML.Constraint.specification) in list(
        dispatcher._handlers.keys()
    )


def test_notification_of_change(
    dispatcher, uml_transition, uml_constraint, event, element_factory
):
    """
    Test notifications with Transition object.
    """
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
    """
    Test unregister with composition. Use Class.ownedOperation.precondition.
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
    """
    Test unregister with composition. Use Class.ownedOperation.precondition.
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


class A(Element):
    def __init__(self, id=None, event_handler=None):
        super().__init__(id, event_handler)


A.one = association("one", A, lower=0, upper=1, composite=True)
A.two = association("two", A, lower=0, upper=2, composite=True)


class ElementDispatcherAsServiceTestCase(TestCase):
    def A(self):
        return self.element_factory.create(A)

    def setUp(self):
        super(ElementDispatcherAsServiceTestCase, self).setUp()
        self.events = []
        self.dispatcher = self.element_factory.element_dispatcher

    def tearDown(self):
        super(ElementDispatcherAsServiceTestCase, self).tearDown()

    def _handler(self, event):
        self.events.append(event)

    def test_notification(self):
        """
        Test notifications with Class object.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Class)
        o = element.ownedOperation = self.element_factory.create(UML.Operation)
        p = element.ownedOperation[0].formalParameter = self.element_factory.create(
            UML.Parameter
        )
        p.name = "func"
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert len(dispatcher._handlers) == 3
        assert not self.events

        element.ownedOperation = self.element_factory.create(UML.Operation)
        assert len(self.events) == 1, self.events
        assert len(dispatcher._handlers) == 4

        p.name = "othername"
        assert len(self.events) == 2, self.events

        del element.ownedOperation[o]
        assert len(dispatcher._handlers) == 2

    def test_association_notification(self):
        """
        Test notifications with Class object.

        Tricky case where no events are fired.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Association)
        p1 = element.memberEnd = self.element_factory.create(UML.Property)
        p2 = element.memberEnd = self.element_factory.create(UML.Property)

        assert len(element.memberEnd) == 2
        dispatcher.subscribe(self._handler, element, "memberEnd.name")
        assert len(dispatcher._handlers) == 3, len(dispatcher._handlers)
        assert not self.events

        p1.name = "foo"
        assert len(self.events) == 1, (self.events, dispatcher._handlers)
        assert len(dispatcher._handlers) == 3

        p1.name = "othername"
        assert len(self.events) == 2, self.events

        p1.name = "othername"
        assert len(self.events) == 2, self.events

    def test_association_notification_complex(self):
        """
        Test notifications with Class object.

        Tricky case where no events are fired.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Association)
        p1 = element.memberEnd = self.element_factory.create(UML.Property)
        p2 = element.memberEnd = self.element_factory.create(UML.Property)
        p1.lowerValue = "0"
        p1.upperValue = "1"
        p2.lowerValue = "1"
        p2.upperValue = "*"

        assert len(element.memberEnd) == 2

        base = "memberEnd<Property>."
        dispatcher.subscribe(self._handler, element, base + "name")
        dispatcher.subscribe(self._handler, element, base + "aggregation")
        dispatcher.subscribe(self._handler, element, base + "classifier")
        dispatcher.subscribe(self._handler, element, base + "lowerValue")
        dispatcher.subscribe(self._handler, element, base + "upperValue")

        assert len(dispatcher._handlers) == 11, len(dispatcher._handlers)
        assert not self.events

        p1.name = "foo"
        assert len(self.events) == 1, (self.events, dispatcher._handlers)
        assert len(dispatcher._handlers) == 11

        p1.name = "othername"
        assert len(self.events) == 2, self.events

    def test_diamond(self):
        """
        Test diamond shaped dependencies a -> b -> c, a -> b' -> c
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self.dispatcher, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.subscribe_all()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = A()
        a.one.two[1].one = a.one.two[0].one
        a.one.two[0].one.two = A()

        assert 6 == len(self.events)

        a.unlink()
        watcher.unsubscribe_all()
        watcher.unsubscribe_all()

    def test_big_diamond(self):
        """
        Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' -> d
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self.dispatcher, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.subscribe_all()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = A()
        a.one.two[1].one = A()
        a.one.two[0].one.two = A()
        a.one.two[1].one.two = a.one.two[0].one.two[0]

        assert 7 == len(self.events)

        a.unlink()
        watcher.unsubscribe_all()
        watcher.unsubscribe_all()
        assert 0 == len(self.dispatcher._handlers)

    def test_braking_big_diamond(self):
        """
        Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' -> d
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self.dispatcher, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.subscribe_all()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = A()
        a.one.two[1].one = A()
        a.one.two[0].one.two = A()
        a.one.two[1].one.two = a.one.two[0].one.two[0]

        assert 7 == len(self.events)
        assert 6 == len(self.dispatcher._handlers)

        del a.one.two[0].one
        # a.unlink()
        watcher.unsubscribe_all()
        watcher.unsubscribe_all()
        assert 0 == len(self.dispatcher._handlers)

    def test_cyclic(self):
        """
        Test cyclic dependency a -> b -> c -> a.
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self.dispatcher, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.subscribe_all()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = a

        assert 4 == len(self.events)

        # a.one.two[0].one.two = A()
        # a.one.two[0].one.two = A()

        a.unlink()
        assert 1 == len(self.dispatcher._handlers)
