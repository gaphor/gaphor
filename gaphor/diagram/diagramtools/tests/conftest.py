import pytest
from gaphas.painter import BoundingBoxPainter
from gaphas.view import GtkView

from gaphor.diagram.painter import ItemPainter
from gaphor.diagram.selection import Selection
from gaphor.diagram.tests.fixtures import diagram, element_factory, event_manager


@pytest.fixture
def view(diagram):
    view = GtkView(model=diagram, selection=Selection())
    view._qtree.resize((-100, -100, 400, 400))
    item_painter = ItemPainter(view.selection)
    view.painter = item_painter
    view.bounding_box_painter = BoundingBoxPainter(item_painter)
    return view
