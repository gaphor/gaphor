
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.application import Application

class ClassBasedDispatcherTestCase(TestCase):

    services = ['element_factory', 'class_based_dispatcher']

    def setUp(self):
        super(ClassBasedDispatcherTestCase, self).setUp()
        self.events = []
        self.dispatcher = Application.get_service('class_based_dispatcher')

    def tearDown(self):
        self.dispatcher.unregister_handler(self._handler, UML.Class)

    def _handler(self, event):
        self.events.append(event)

    def test_dispatcher(self):
        self.dispatcher.register_handler(self._handler, UML.Class)
        c = self.element_factory.create(UML.Class)

        # Create event
        assert len(self.events) == 1, self.events

        c.name = 'name'

        # AttributeChange event
        assert len(self.events) == 2, self.events

        p = self.element_factory.create(UML.Package)
        p.name = 'name'

        # No change
        assert len(self.events) == 2, self.events

        self.dispatcher.unregister_handler(self._handler, UML.Class)

        c.name = 'blah'

        # No change
        assert len(self.events) == 2, self.events


    def test_dispatcher_inherited_classes(self):
        self.dispatcher.register_handler(self._handler, UML.Classifier)
        c = self.element_factory.create(UML.Class)

        # Create event
        assert len(self.events) == 1, self.events

        c.name = 'name'

        # AttributeChange event
        assert len(self.events) == 2, self.events

        p = self.element_factory.create(UML.Package)
        p.name = 'name'

        # No change
        assert len(self.events) == 2, self.events

        self.dispatcher.unregister_handler(self._handler, UML.Classifier)

        c.name = 'blah'

        # No change
        assert len(self.events) == 2, self.events


# vim: sw=4:et:ai
