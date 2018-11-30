from gi.repository import Gtk
from gaphor import UML
from gaphor.diagram import items
from gaphor.tests import TestCase
from gaphor.adapters.propertypages import ClassAttributes


class ClassAttributesTestCase(TestCase):
    def test_attribute_editing(self):
        class_item = self.create(items.ClassItem, UML.Class)
        model = ClassAttributes(class_item, (str, bool, object))
        model.append([None, False, None])
        path = Gtk.TreePath.new_first()
        iter = model.get_iter(path)
        model.set_value(iter, col=0, value="attr")

        assert model[iter][-1] is class_item.subject.ownedAttribute[0]
