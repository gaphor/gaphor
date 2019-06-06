"""
Test basic diagram item functionality like styles, etc.
"""

import pytest
from gaphor import Application
from gaphor.diagram.diagramitem import DiagramItem


@pytest.fixture
def application(services=["event_manager", "component_registry", "element_factory"]):
    Application.init(services=services)
    yield Application
    Application.shutdown()


@pytest.fixture
def ItemA(application):
    class ItemA(DiagramItem):
        __style__ = {"a-01": 1, "a-02": 2}

    return ItemA


def test_style_assign(ItemA):
    """
    Test style assign
    """
    item_a = ItemA()

    assert ItemA.style.a_01 == 1
    assert ItemA.style.a_02 == 2
    assert item_a.style.a_01 == 1
    assert item_a.style.a_02 == 2


def test_style_override(ItemA):
    """
    Test style override
    """

    class ItemB(ItemA):
        __style__ = {"b-01": 3, "b-02": 4, "a-01": 5}

    item_b = ItemB()
    assert ItemB.style.b_01 == 3
    assert ItemB.style.b_02 == 4
    assert ItemB.style.a_01 == 5
    assert ItemB.style.a_02 == 2
    assert item_b.style.b_01 == 3
    assert item_b.style.b_02 == 4
    assert item_b.style.a_01 == 5
    assert item_b.style.a_02 == 2

    # check ItemA style, it should remain unaffected by ItemB style
    # changes
    assert ItemA.style.a_01 == 1
    assert ItemA.style.a_02 == 2
