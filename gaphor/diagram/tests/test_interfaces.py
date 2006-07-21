"""
Test Interfaces.
"""

import unittest
from zope import interface
from gaphor import diagram


class InterfacesTestCase(unittest.TestCase):

    def test_comment(self):
        self.assertTrue(diagram.interfaces.ICommentItem.implementedBy(diagram.comment.CommentItem))
        item = diagram.comment.CommentItem()
        editor = diagram.interfaces.IEditor(item)
        self.assertTrue(editor)
        self.assertTrue(editor._item is item)
        

# vim: sw=4:et
