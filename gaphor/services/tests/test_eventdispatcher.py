
from gaphor.tests import TestCase
from zope import component
from gaphor.application import Application
from gaphor.UML import *
from gaphor.UML.interfaces import *


class ElementFactoryTestCase(TestCase):

    services = TestCase.services + ['event_dispatcher']


    def test_element_event(self):
        events = []
        @component.adapter(Class, IElementChangeEvent)
        def handler(element, event, events=events):
            assert element is event.element
            events.append(event)

        #Application.init_components()
        Application.register_handler(handler)

        try:
            c = Class()
            del events[:]
            c.name = 'name'
            assert len(events) == 1, events
            assert events[0].new_value == 'name'
        finally:
            Application.unregister_handler(handler)


# vim:sw=4:et:ai
