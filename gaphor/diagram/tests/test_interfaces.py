"""
Test Interfaces.
"""

import unittest
from zope import interface
from gaphor import diagram
from gaphor import diagram

# Ensure adapters are available
import gaphor.adapters
reload(gaphor.adapters.editors)
reload(gaphor.adapters.connectors)


class InterfacesTestCase(unittest.TestCase):

    def test_comment(self):
        #self.assertTrue(diagram.interfaces.ICommentItem.implementedBy(diagram.comment.CommentItem))
        item = diagram.comment.CommentItem()
        editor = diagram.interfaces.IEditor(item)
        self.assertTrue(editor)
        self.assertTrue(editor._item is item)
        

# vim: sw=4:et
