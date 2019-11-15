"""
Formatting of UML model elements into text tests.
"""

import pytest

import gaphor.UML.uml2 as UML
from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umlfmt import format


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def test_simple_format(factory):
    """Test simple attribute formatting
    """
    a = factory.create(UML.Property)
    a.name = "myattr"
    assert "+ myattr" == format(a)

    a.typeValue = "int"
    assert "+ myattr: int" == format(a)
