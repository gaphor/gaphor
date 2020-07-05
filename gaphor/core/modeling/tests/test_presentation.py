import pytest
from gaphas.item import Item

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.core.modeling.presentation import Presentation


class StubItem(Presentation, Item):
    pass


@pytest.fixture
def element_factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)
