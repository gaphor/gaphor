from gi.repository import Gtk

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.editors import Editor
from gaphor.diagram.classes import ClassItem, AssociationItem
from gaphor.diagram.classes.classespropertypages import AttributesPage, OperationsPage


class EditorTestCase(TestCase):
    def test_association_editor(self):
        assoc = self.create(AssociationItem)
        adapter = Editor(assoc)
        assert not adapter.is_editable(10, 10)
        assert adapter._edit is None

        # Intermezzo: connect the association between two classes
        class1 = self.create(ClassItem, UML.Class)
        class2 = self.create(ClassItem, UML.Class)

        assoc.handles()[0].pos = 10, 10
        assoc.handles()[-1].pos = 100, 100
        self.connect(assoc, assoc.head, class1)
        self.connect(assoc, assoc.tail, class2)
        assert assoc.subject

        # Now the association has a subject member, so editing should really
        # work.
        pos = 55, 55
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc)

        pos = assoc.head_end._name_bounds[:2]
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc.head_end)

        pos = assoc.tail_end._name_bounds[:2]
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc.tail_end)

    def test_classifier_editor(self):
        """
        Test classifier editor
        """
        klass = self.create(ClassItem, UML.Class)
        klass.subject.name = "Class1"

        self.diagram.canvas.update()

        attr = self.element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = self.element_factory.create(UML.Operation)
        oper.name = "method"
        klass.subject.ownedOperation = oper

        self.diagram.canvas.update()

        edit = Editor(klass)

        self.assertEqual("CompartmentItemEditor", edit.__class__.__name__)

        self.assertEqual(True, edit.is_editable(10, 10))

        # Test the inner working of the editor
        self.assertEqual(klass, edit._edit)
        self.assertEqual("Class1", edit.get_text())

        # The attribute:
        y = klass._header_size[1] + klass.style.compartment_padding[0] + 3
        self.assertEqual(True, edit.is_editable(4, y))
        self.assertEqual(attr, edit._edit.subject)
        self.assertEqual("+ blah", edit.get_text())

        y += klass.compartments[0].height
        # The operation
        self.assertEqual(True, edit.is_editable(3, y))
        self.assertEqual(oper, edit._edit.subject)
        self.assertEqual("+ method()", edit.get_text())

    def test_class_attribute_editor(self):
        klass = self.create(ClassItem, UML.Class)
        klass.subject.name = "Class1"

        editor = AttributesPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        self.assertSame(Gtk.TreeView, type(tree_view))

        attr = self.element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        self.assertSame(attr, tree_view.get_model()[0][-1])
        self.assertEqual("+ blah", tree_view.get_model()[0][0])

        attr.name = "foo"
        self.assertEqual("+ foo", tree_view.get_model()[0][0])
        attr.typeValue = "int"
        self.assertEqual("+ foo: int", tree_view.get_model()[0][0])
        attr.isDerived = True
        self.assertEqual("+ /foo: int", tree_view.get_model()[0][0])
        page.destroy()

    def test_class_operation_editor(self):
        klass = self.create(ClassItem, UML.Class)
        klass.subject.name = "Class1"

        editor = OperationsPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        self.assertSame(Gtk.TreeView, type(tree_view))

        oper = self.element_factory.create(UML.Operation)
        oper.name = "o"
        klass.subject.ownedOperation = oper

        self.assertSame(oper, tree_view.get_model()[0][-1])
        self.assertEqual("+ o()", tree_view.get_model()[0][0])
        p = self.element_factory.create(UML.Parameter)
        p.name = "blah"
        oper.formalParameter = p
        self.assertEqual("+ o(in blah)", tree_view.get_model()[0][0])

        page.destroy()
