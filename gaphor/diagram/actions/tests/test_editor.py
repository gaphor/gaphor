from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.actions import ObjectNodeItem
from gaphor.diagram.editors import Editor


class EditorTestCase(TestCase):
    def setUp(self):
        super(EditorTestCase, self).setUp()

    def test_objectnode_editor(self):
        node = self.create(ObjectNodeItem, UML.ObjectNode)
        self.diagram.canvas.update_now()

        adapter = Editor(node)
        self.assertTrue(adapter.is_editable(10, 10))
        # assert not adapter.edit_tag

        # assert adapter.is_editable(*node.tag_bounds[:2])
        # assert adapter.edit_tag
