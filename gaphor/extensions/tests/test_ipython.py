from gaphor.extensions.ipython import draw
from gaphor.UML import Diagram


def test_draw(element_factory):
    diagram = element_factory.create(Diagram)

    svg = draw(diagram)

    assert svg
