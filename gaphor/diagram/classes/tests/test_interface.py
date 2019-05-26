"""
Test classes.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.classes.interface import InterfaceItem


class InterfaceTestCase(TestCase):
    def test_interface_creation(self):
        """Test interface creation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        assert isinstance(iface.subject, UML.Interface)

        assert iface._name.is_visible()

        # check style information
        self.assertFalse(iface.style.name_outside)

    def test_changing_to_icon_mode(self):
        """Test interface changing to icon mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.drawing_style = iface.DRAW_ICON

        assert iface.DRAW_ICON == iface.drawing_style

        # default folded mode is provided
        self.assertTrue(iface.FOLDED_PROVIDED, iface.folded)

        # check if style information changed
        self.assertTrue(iface._name.style.text_outside)

        # handles are not movable anymore
        for h in iface.handles():
            assert not h.movable

        # name is visible
        assert iface._name.is_visible()

    def test_changing_to_classifier_mode(self):
        """Test interface changing to classifier mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.drawing_style = iface.DRAW_ICON

        iface.drawing_style = iface.DRAW_COMPARTMENT
        assert iface.DRAW_COMPARTMENT == iface.drawing_style

        # check if style information changed
        self.assertFalse(iface._name.style.text_outside)

        # handles are movable again
        for h in iface.handles():
            assert h.movable

    def test_assembly_connector_icon_mode(self):
        """Test interface in assembly connector icon mode
        """
        iface = self.create(InterfaceItem, UML.Interface)
        assert iface._name.is_visible()

        iface.folded = iface.FOLDED_ASSEMBLY
        assert not iface._name.is_visible()

    def test_folded_interface_persistence(self):
        """Test folded interface saving/loading
        """
        iface = self.create(InterfaceItem, UML.Interface)

        # note: assembly folded mode..
        iface.folded = iface.FOLDED_REQUIRED

        data = self.save()
        self.load(data)

        interfaces = self.diagram.canvas.select(lambda e: isinstance(e, InterfaceItem))
        assert 1 == len(interfaces)
        # ... gives provided folded mode on load;
        # correct folded mode is determined by connections, which will be
        # recreated later, i.e. required folded mode will be set when
        # implementation connects to the interface
        self.assertEqual(iface.FOLDED_PROVIDED, interfaces[0].folded)
