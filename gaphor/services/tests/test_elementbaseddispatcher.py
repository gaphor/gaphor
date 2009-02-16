
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.application import Application
from gaphor.services.elementbaseddispatcher import ElementBasedDispatcher


class ElementBasedDispatcherTestCase(TestCase):

    def setUp(self):
        super(ElementBasedDispatcherTestCase, self).setUp()
        self.events = []
        self.dispatcher = ElementBasedDispatcher()

    def tearDown(self):
        super(ElementBasedDispatcherTestCase, self).tearDown()

    def _handler(self, event):
        self.events.append(event)


    def test_register_handler(self):
        dispatcher = ElementBasedDispatcher()
        element = UML.Class()
        def handler(event): print 'Handled', event.element
        dispatcher.register_handler(element, 'ownedOperation.parameter.name', handler)
        assert len(dispatcher._handlers) == 1
        assert dispatcher._handlers.keys()[0] == (element, UML.Class.ownedOperation)

        # Add some properties:

        element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(element, 'ownedOperation.parameter.name', handler)
        assert len(dispatcher._handlers) == 3

    def test_unregister_handler(self):

        # First some setup:
        dispatcher = ElementBasedDispatcher()
        element = UML.Class()
        def handler(event): print 'Handled', event.element
        o = element.ownedOperation = UML.Operation()
        p = element.ownedOperation[0].formalParameter = UML.Parameter()
        p.name = 'func'
        dispatcher.register_handler(element, 'ownedOperation.parameter.name', handler)
        assert len(dispatcher._handlers) == 3
        assert dispatcher._handlers[o, UML.Operation.parameter]

        dispatcher.unregister_handler(o, UML.Operation.parameter, handler)

        assert len(dispatcher._handlers) == 1, dispatcher._handlers
        assert dispatcher._handlers.keys()[0] == (element, UML.Class.ownedOperation)

# vim: sw=4:et:ai
