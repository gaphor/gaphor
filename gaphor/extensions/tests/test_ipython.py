from gaphor.core.modeling import Diagram
from gaphor.extensions.ipython import draw


def test_draw(element_factory):
    diagram = element_factory.create(Diagram)

    svg = draw(diagram)

    assert svg
