"""
Test if the collection's list supports all trickery.
"""

import pytest

from gaphor.core.modeling.collection import collection, collectionlist


class MockElement:
    def __init__(self):
        self.events = []

    def handle(self, event):
        self.events.append(event)


class MockProperty:
    def __init__(self):
        self.values = []

    def _set(self, object, value):
        self.values.append((object, value))


def test_listing():
    c: collectionlist[str] = collectionlist()
    c.append("a")
    c.append("b")
    c.append("c")
    assert str(c) == "['a', 'b', 'c']"


def test_append():
    p = MockProperty()
    o = object()
    c = collection(p, o, str)
    c.append("s")

    assert p.values == [(o, "s")]


def test_append_wrong_type():
    c = collection(None, None, int)

    with pytest.raises(TypeError):
        c.append("s")  # type: ignore[arg-type]


def test_size():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert c.size() == 2


def test_includes():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert c.includes(1)
    assert not c.includes(3)


def test_excludes():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert not c.excludes(1)
    assert c.excludes(3)


def test_count():
    c = collection(None, None, int)
    c.items = [1, 2, 2]  # type: ignore[assignment]

    assert c.count(1) == 1
    assert c.count(2) == 2
    assert c.count(3) == 0


def test_includesAll():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert c.includesAll([1])
    assert not c.includesAll([3])


def test_excludesAll():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert not c.excludesAll([1])
    assert c.excludesAll([3])


def test_select():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert c.select(lambda e: e > 1) == [2]


def test_reject():
    c = collection(None, None, int)
    c.items = [1, 2]  # type: ignore[assignment]

    assert c.reject(lambda e: e > 1) == [1]


def test_collect():
    c = collection(None, None, int)
    c.items = [1, 2, 3]  # type: ignore[assignment]

    assert c.collect(lambda e: e * e) == [1, 4, 9]


def test_empty():
    c = collection(None, None, int)

    assert c.isEmpty()


def test_not_empty():
    c: collection[int] = collection(None, None, int)
    c.items = [1, 2, 3]  # type: ignore[assignment]

    assert not c.isEmpty()


def test_swap():
    o = MockElement()
    c: collection[str] = collection(None, o, str)
    c.items = ["a", "b", "c"]  # type: ignore[assignment]
    c.swap("a", "c")
    assert c.items == ["c", "b", "a"]
    assert o.events
