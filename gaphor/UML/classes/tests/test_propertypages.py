from gi.repository import Gtk

from gaphor import UML
from gaphor.UML.classes import EnumerationItem
from gaphor.UML.classes.classespropertypages import (
    ClassEnumerationLiterals,
)


def test_enumeration_editing(create):
    enum_item = create(EnumerationItem, UML.Enumeration)
    model = ClassEnumerationLiterals(enum_item)
    model.append([None, None])
    path = Gtk.TreePath.new_first()
    iter = model.get_iter(path)
    model.update(iter, col=0, value="enum")

    assert model[iter][-1] is enum_item.subject.ownedLiteral[0]
