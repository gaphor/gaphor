from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.classes import ClassItem
from gaphor.diagram.classes.classespropertypages import ClassAttributes
from gaphor.tests import TestCase


class ClassPropertyPagesTestCase(TestCase):
    def test_attribute_editing(self):
        class_item = self.create(ClassItem, UML.Class)
        model = ClassAttributes(class_item, (str, bool, object))
        model.append([None, False, None])
        path = Gtk.TreePath.new_first()
        iter = model.get_iter(path)
        model.update(iter, col=0, value="attr")

        assert model[iter][-1] is class_item.subject.ownedAttribute[0]
