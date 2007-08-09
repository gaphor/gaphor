
from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IEditor

class EditorTestCase(TestCase):

    services = ['element_factory', 'adapter_loader']

    def setUp(self):
        super(EditorTestCase, self).setUp()
        self.factory = self.get_service('element_factory')


    def test_association_editor(self):
        diagram = self.factory.create(UML.Diagram)
        assoc = diagram.create(items.AssociationItem)
        adapter = IEditor(assoc)
        assert not adapter.is_editable(10, 10)
        assert adapter._edit is None

        # Intermezzo: connect the association between two classes
        class1 = diagram.create(items.ClassItem, subject=self.factory.create(UML.Class))
        class2 = diagram.create(items.ClassItem, subject=self.factory.create(UML.Class))
        from gaphor.interfaces import IService
        component.provideUtility(self.factory, IService, 'element_factory')

        from gaphor.diagram.interfaces import IConnect
        connector = component.queryMultiAdapter((class1, assoc), IConnect)
        assoc.handles()[0].pos = 10, 10
        connector.connect(assoc.handles()[0])
        assert assoc.handles()[0].connected_to
        connector = component.queryMultiAdapter((class2, assoc), IConnect)
        assoc.handles()[-1].pos = 100, 100
        connector.connect(assoc.handles()[-1])
        assert assoc.handles()[-1].connected_to
        assert assoc.subject

        # Now the association has a subject member, so editing should really
        # work.
        assert adapter.is_editable(55, 55)
        assert adapter._edit is assoc

        x, y = assoc.head_end._name_bounds[:2]
        assert adapter.is_editable(x, y)
        assert adapter._edit is assoc.head_end
        
        x, y = assoc.tail_end._name_bounds[:2]
        assert adapter.is_editable(x, y)
        assert adapter._edit is assoc.tail_end
        
    def test_objectnode_editor(self):
        diagram = self.factory.create(UML.Diagram)
        node = diagram.create(items.ObjectNodeItem, subject=self.factory.create(UML.ObjectNode))
        diagram.canvas.update_now()

        adapter = IEditor(node)
        assert adapter.is_editable(10, 10)
        #assert not adapter.edit_tag

        #assert adapter.is_editable(*node.tag_bounds[:2])
        #assert adapter.edit_tag


    def test_classifier_editor(self):
        """
        Test classifier editor
        """
        diagram = self.factory.create(UML.Diagram)
        klass = diagram.create(items.ClassItem, subject=self.factory.create(UML.Class))
        klass.subject.name = 'Class1'

        diagram.canvas.update()

        attr = self.factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = self.factory.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        diagram.canvas.update()

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


# vim:sw=4:et:ai
