"""
Test classes.
"""

from zope import component
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.classes.interface import InterfaceItem


class InterfaceTestCase(TestCase):
    def test_interface_creation(self):
        """Test interface creation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        self.assertTrue(isinstance(iface.subject, UML.Interface))

        self.assertTrue(iface._name.is_visible())

        # check style information
        self.assertFalse(iface.style.name_outside)


    def test_changing_to_icon_mode(self):
        """Test interface changing to icon mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.drawing_style = iface.DRAW_ICON
        self.assertEquals(iface.DRAW_ICON, iface.drawing_style)

        # check if style information changed
        self.assertTrue(iface._name.style.text_outside)

        # handles are not movable anymore
        for h in iface.handles():
            self.assertFalse(h.movable)

        # name is visible
        self.assertTrue(iface._name.is_visible())


    def test_changing_to_classifier_mode(self):
        """Test interface changing to classifier mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.drawing_style = iface.DRAW_ICON

        iface.drawing_style = iface.DRAW_COMPARTMENT
        self.assertEquals(iface.DRAW_COMPARTMENT, iface.drawing_style)

        # check if style information changed
        self.assertFalse(iface._name.style.text_outside)

        # handles are movable again
        for h in iface.handles():
            self.assertTrue(h.movable)


    def test_assembly_connector_icon_mode(self):
        """Test interface in assembly connector icon mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        assert iface._name.is_visible()

        iface.folded = iface.FOLDED_ASSEMBLY
        self.assertFalse(iface._name.is_visible())



# vim:sw=4:et:ai
