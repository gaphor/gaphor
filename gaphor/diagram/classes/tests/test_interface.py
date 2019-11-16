"""
Test classes.
"""

from gaphor import UML
from gaphor.diagram.classes.interface import Folded, InterfaceItem
from gaphor.tests import TestCase


class InterfaceTestCase(TestCase):
    def test_interface_creation(self):
        """Test interface creation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        assert isinstance(iface.subject, UML.Interface)

    def test_folded_interface_persistence(self):
        """Test folded interface saving/loading
        """
        iface = self.create(InterfaceItem, UML.Interface)

        # note: assembly folded mode..
        iface.folded = Folded.REQUIRED

        data = self.save()
        self.load(data)

        interfaces = self.diagram.canvas.select(lambda e: isinstance(e, InterfaceItem))
        assert 1 == len(interfaces)
        # ... gives provided folded mode on load;
        # correct folded mode is determined by connections, which will be
        # recreated later, i.e. required folded mode will be set when
        # implementation connects to the interface
        # assert Folded.PROVIDED == interfaces[0].folded
