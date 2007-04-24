
from unittest import TestCase
from zope import component
from gaphor import UML
from gaphor.UML.elementfactory import ElementFactory
from gaphor.diagram import items
from gaphor.diagram.interfaces import IEditor

# ensure adapters are registered
import gaphor.adapters


class EditorTestCase(TestCase):

    def setUp(self):
        self.factory = ElementFactory()
        self.factory.init(None)

    def tearDown(self):
        self.factory.shutdown()

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
        connector.connect(assoc.handles()[0], 10, 10)
        assert assoc.handles()[0].connected_to
        connector = component.queryMultiAdapter((class2, assoc), IConnect)
        connector.connect(assoc.handles()[-1], 100, 100)
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
        assert not adapter.edit_tag

        assert adapter.is_editable(*node.tag_bounds[:2])
        assert adapter.edit_tag


