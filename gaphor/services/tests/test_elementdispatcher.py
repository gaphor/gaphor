import unittest
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.application import Application
from gaphor.services.elementdispatcher import ElementDispatcher
from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactoryService


class ElementDispatcherTestCase(unittest.TestCase):
    def setUp(self):
        self.events = []
        event_manager = EventManager()
        self.element_factory = ElementFactoryService(event_manager)
        self.dispatcher = ElementDispatcher(event_manager)

    def tearDown(self):
        self.dispatcher.shutdown()

    def _handler(self, event):
        self.events.append(event)

    def test_register_handler(self):
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Class)
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert len(dispatcher._handlers) == 1
        assert list(dispatcher._handlers.keys())[0] == (
            element,
            UML.Class.ownedOperation,
        )

        # Add some properties:

        # 1:
        element.ownedOperation = self.element_factory.create(UML.Operation)
        # 2:
        p = element.ownedOperation[0].formalParameter = self.element_factory.create(
            UML.Parameter
        )
        # 3:
        p.name = "func"
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert 3 == len(self.events)
        assert 3 == len(dispatcher._handlers)

    def test_register_handler_twice(self):
        """
        Multiple registrations have no effect.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Class)

        # Add some properties:

        element.ownedOperation = self.element_factory.create(UML.Operation)
        p = element.ownedOperation[0].formalParameter = self.element_factory.create(
            UML.Parameter
        )
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")

        n_handlers = len(dispatcher._handlers)

        assert 0 == len(self.events)
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert n_handlers == len(dispatcher._handlers)
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert n_handlers == len(dispatcher._handlers)
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert n_handlers == len(dispatcher._handlers)

        p.name = "func"
        assert 1 == len(self.events)

    def test_unregister_handler(self):

        # First some setup:
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Class)
        o = element.ownedOperation = self.element_factory.create(UML.Operation)
        p = element.ownedOperation[0].formalParameter = self.element_factory.create(
            UML.Parameter
        )
        p.name = "func"
        dispatcher.subscribe(self._handler, element, "ownedOperation.parameter.name")
        assert len(dispatcher._handlers) == 3
        assert dispatcher._handlers[element, UML.Class.ownedOperation]
        assert dispatcher._handlers[o, UML.Operation.parameter]
        assert dispatcher._handlers[p, UML.Parameter.name]

        dispatcher.unsubscribe(self._handler)

        assert len(dispatcher._handlers) == 0, dispatcher._handlers
        assert len(dispatcher._reverse) == 0, dispatcher._reverse
        # assert dispatcher._handlers.keys()[0] == (element, UML.Class.ownedOperation)
        # Should not fail here too:
        dispatcher.unsubscribe(self._handler)

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

    def test_notification_2(self):
        """
        Test notifications with Transition object.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Transition)
        g = element.guard = self.element_factory.create(UML.Constraint)
        dispatcher.subscribe(self._handler, element, "guard.specification")
        assert len(dispatcher._handlers) == 2
        assert not self.events
        assert (element.guard, UML.Constraint.specification) in list(
            dispatcher._handlers.keys()
        ), list(dispatcher._handlers.keys())

        g.specification = "x"
        assert len(self.events) == 1, self.events

        element.guard = self.element_factory.create(UML.Constraint)
        assert len(self.events) == 2, self.events
        assert len(dispatcher._handlers) == 2, len(dispatcher._handlers)
        assert (element.guard, UML.Constraint.specification) in list(
            dispatcher._handlers.keys()
        )

    def test_notification_of_change(self):
        """
        Test notifications with Transition object.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Transition)
        g = element.guard = self.element_factory.create(UML.Constraint)
        dispatcher.subscribe(self._handler, element, "guard.specification")
        assert len(dispatcher._handlers) == 2
        assert not self.events

        g.specification = "x"
        assert len(self.events) == 1, self.events

        element.guard = self.element_factory.create(UML.Constraint)
        assert len(self.events) == 2, self.events

    def test_notification_with_composition(self):
        """
        Test unregister with composition. Use Class.ownedOperation.precondition.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Class)
        o = element.ownedOperation = self.element_factory.create(UML.Operation)
        p = element.ownedOperation[0].precondition = self.element_factory.create(
            UML.Constraint
        )
        p.name = "func"
        dispatcher.subscribe(self._handler, element, "ownedOperation.precondition.name")
        assert len(dispatcher._handlers) == 3
        assert not self.events

        del element.ownedOperation[o]
        assert len(dispatcher._handlers) == 1

    def test_notification_with_incompatible_elements(self):
        """
        Test unregister with composition. Use Class.ownedOperation.precondition.
        """
        dispatcher = self.dispatcher
        element = self.element_factory.create(UML.Transition)
        g = element.guard = self.element_factory.create(UML.Constraint)
        dispatcher.subscribe(self._handler, element, "guard.specification")
        assert len(dispatcher._handlers) == 2
        assert not self.events
        assert (element.guard, UML.Constraint.specification) in list(
            dispatcher._handlers.keys()
        ), list(dispatcher._handlers.keys())

        g.specification = "x"
        assert len(self.events) == 1, self.events

        g.specification = "a"
        assert len(self.events) == 2, self.events


from gaphor.UML import Element
from gaphor.UML.properties import association
from gaphor.services.elementdispatcher import EventWatcher


class A(Element):
    def __init__(self, id=None, event_handler=None):
        super().__init__(id, event_handler)


A.one = association("one", A, lower=0, upper=1, composite=True)
A.two = association("two", A, lower=0, upper=2, composite=True)


class ElementDispatcherAsServiceTestCase(TestCase):

    services = TestCase.services + ["element_dispatcher"]

    def A(self):
        return self.element_factory.create(A)

    def setUp(self):
        super(ElementDispatcherAsServiceTestCase, self).setUp()
        self.events = []
        self.dispatcher = Application.get_service("element_dispatcher")

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
        watcher = EventWatcher(a, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.register_handlers()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = A()
        a.one.two[1].one = a.one.two[0].one
        a.one.two[0].one.two = A()

        assert 6 == len(self.events)

        a.unlink()
        watcher.unregister_handlers()
        watcher.unregister_handlers()

    def test_big_diamond(self):
        """
        Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' -> d
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.register_handlers()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = A()
        a.one.two[1].one = A()
        a.one.two[0].one.two = A()
        a.one.two[1].one.two = a.one.two[0].one.two[0]

        assert 7 == len(self.events)

        a.unlink()
        watcher.unregister_handlers()
        watcher.unregister_handlers()
        assert 0 == len(self.dispatcher._handlers)

    def test_braking_big_diamond(self):
        """
        Test diamond shaped dependencies a -> b -> c -> d, a -> b' -> c' -> d
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.register_handlers()

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
        watcher.unregister_handlers()
        watcher.unregister_handlers()
        assert 0 == len(self.dispatcher._handlers)

    def test_cyclic(self):
        """
        Test cyclic dependency a -> b -> c -> a.
        """
        A = self.A
        a = A()
        watcher = EventWatcher(a, self._handler)
        watcher.watch("one.two.one.two")
        # watcher.watch('one.one.one.one')
        watcher.register_handlers()

        a.one = A()
        a.one.two = A()
        a.one.two = A()
        a.one.two[0].one = a

        assert 4 == len(self.events)

        # a.one.two[0].one.two = A()
        # a.one.two[0].one.two = A()

        a.unlink()
        assert 1 == len(self.dispatcher._handlers)


# vim: sw=4:et:ai
