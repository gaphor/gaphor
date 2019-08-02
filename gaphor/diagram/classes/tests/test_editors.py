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
        assert adapter.is_editable(*pos)
        assert adapter._edit is assoc

        pos = assoc.head_end._name_bounds[:2]
        assert adapter.is_editable(*pos)
        assert adapter._edit is assoc.head_end

        pos = assoc.tail_end._name_bounds[:2]
        assert adapter.is_editable(*pos)
        assert adapter._edit is assoc.tail_end

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

        assert "CompartmentItemEditor" == edit.__class__.__name__

        assert edit.is_editable(10, 10)

        # Test the inner working of the editor
        self.assertEqual(klass, edit._edit)
        assert "Class1" == edit.get_text()

    def test_class_attribute_editor(self):
        klass = self.create(ClassItem, UML.Class)
        klass.subject.name = "Class1"

        editor = AttributesPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        assert Gtk.TreeView is type(tree_view)

        attr = self.element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        assert attr is tree_view.get_model()[0][-1]
        assert "+ blah" == tree_view.get_model()[0][0]

        attr.name = "foo"
        assert "+ foo" == tree_view.get_model()[0][0]
        attr.typeValue = "int"
        assert "+ foo: int" == tree_view.get_model()[0][0]
        attr.isDerived = True
        assert "+ /foo: int" == tree_view.get_model()[0][0]
        page.destroy()

    def test_class_operation_editor(self):
        klass = self.create(ClassItem, UML.Class)
        klass.subject.name = "Class1"

        editor = OperationsPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        assert Gtk.TreeView is type(tree_view)

        oper = self.element_factory.create(UML.Operation)
        oper.name = "o"
        klass.subject.ownedOperation = oper

        assert oper is tree_view.get_model()[0][-1]
        assert "+ o()" == tree_view.get_model()[0][0]
        p = self.element_factory.create(UML.Parameter)
        p.name = "blah"
        oper.formalParameter = p
        assert "+ o(in blah)" == tree_view.get_model()[0][0]

        page.destroy()
