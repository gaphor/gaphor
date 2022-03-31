"""Test classes."""

from gaphor import UML
from gaphor.UML.classes.interface import Folded, InterfaceItem


def test_interface_creation(create):
    """Test interface creation."""
    iface = create(InterfaceItem, UML.Interface)
    assert isinstance(iface.subject, UML.Interface)


def test_folded_interface_persistence(create, loader, saver, element_factory):
    """Test folded interface saving/loading."""
    iface = create(InterfaceItem, UML.Interface)

    # note: assembly folded mode..
    iface.folded = Folded.REQUIRED

    data = saver()
    loader(data)

    interfaces = list(element_factory.select(InterfaceItem))
    assert len(interfaces) == 1
    # ... gives provided folded mode on load;
    # correct folded mode is determined by connections, which will be
    # recreated later, i.e. required folded mode will be set when
    # implementation connects to the interface and Folded.PROVIDED
    # is equal to interfaces[0].folded
