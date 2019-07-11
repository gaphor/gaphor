"""
Test if the collection's list supports all trickery.
"""

from gaphor.UML.collection import collectionlist


def test_listing():
    c = collectionlist()
    c.append("a")
    c.append("b")
    c.append("c")
    assert str(c) == "['a', 'b', 'c']"
