import pytest

from gaphor.core.modeling.element import Element


def test_element_note():
    e = Element()
    e.note = "Hello"

    assert e.note == "Hello"


def test_element_can_not_set_random_property():
    e = Element()

    with pytest.raises(AttributeError):
        e.random_property = 1
