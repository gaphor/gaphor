"""Test classes."""

from gaphor import UML
from gaphor.UML.classes.interface import Folded, InterfaceItem


class TestInterface:
    def test_interface_creation(self, case):
        """Test interface creation."""
        iface = case.create(InterfaceItem, UML.Interface)
        assert isinstance(iface.subject, UML.Interface)

    def test_folded_interface_persistence(self, case):
        """Test folded interface saving/loading."""
        iface = case.create(InterfaceItem, UML.Interface)

        # note: assembly folded mode..
        iface.folded = Folded.REQUIRED

        data = case.save()
        case.load(data)

        interfaces = list(case.diagram.select(InterfaceItem))
        assert len(interfaces) == 1
        # ... gives provided folded mode on load;
        # correct folded mode is determined by connections, which will be
        # recreated later, i.e. required folded mode will be set when
        # implementation connects to the interface and Folded.PROVIDED
        # is equal to interfaces[0].folded
