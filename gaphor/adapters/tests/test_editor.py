
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IEditor
from gaphor.adapters.propertypages import AttributesPage, OperationsPage
import gtk

class EditorTestCase(TestCase):

    def test_association_editor(self):
        assoc = self.create(items.AssociationItem)
        adapter = IEditor(assoc)
        assert not adapter.is_editable(10, 10)
        assert adapter._edit is None

        # Intermezzo: connect the association between two classes
        class1 = self.create(items.ClassItem, UML.Class)
        class2 = self.create(items.ClassItem, UML.Class)

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

        
    def test_objectnode_editor(self):
        node = self.create(items.ObjectNodeItem, UML.ObjectNode)
        self.diagram.canvas.update_now()

        adapter = IEditor(node)
        self.assertTrue(adapter.is_editable(10, 10))
        #assert not adapter.edit_tag

        #assert adapter.is_editable(*node.tag_bounds[:2])
        #assert adapter.edit_tag


    def test_classifier_editor(self):
        """
        Test classifier editor
        """
        klass = self.create(items.ClassItem, UML.Class)
        klass.subject.name = 'Class1'

        self.diagram.canvas.update()

        attr = self.element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = self.element_factory.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        self.diagram.canvas.update()

        edit = IEditor(klass)

        self.assertEqual('ClassifierItemEditor', edit.__class__.__name__)

        self.assertEqual(True, edit.is_editable(10, 10))

        # Test the inner working of the editor
        self.assertEqual(klass, edit._edit)
        self.assertEqual('Class1', edit.get_text())

        # The attribute:
        y = klass._header_size[1] + klass.style.compartment_padding[0] + 3 
        self.assertEqual(True, edit.is_editable(4, y))
        self.assertEqual(attr, edit._edit.subject)
        self.assertEqual('+ blah', edit.get_text())

        y += klass.compartments[0].height
        # The operation
        self.assertEqual(True, edit.is_editable(3, y))
        self.assertEqual(oper, edit._edit.subject)
        self.assertEqual('+ method()', edit.get_text())


    def test_class_attribute_editor(self):
        klass = self.create(items.ClassItem, UML.Class)
        klass.subject.name = 'Class1'
        
        editor = AttributesPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        self.assertSame(gtk.TreeView, type(tree_view))

        attr = self.element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        
# vim:sw=4:et:ai
