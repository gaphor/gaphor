"""
Test Interfaces.
"""

import unittest
from zope import interface
from gaphor import diagram
from gaphor import diagram
from gaphor.tests import TestCase


class InterfacesTestCase(TestCase):
    def test_comment(self):
        # self.assertTrue(diagram.interfaces.ICommentItem.implementedBy(diagram.comment.CommentItem))
        item = diagram.comment.CommentItem()
        editor = diagram.interfaces.Editor(item)
        self.assertTrue(editor)
        self.assertTrue(editor._item is item)


# vim: sw=4:et
