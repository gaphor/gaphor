#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Comment and comment line items connection adapters tests.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items

from gaphor.tests import TestCase

class CommentLineTestCase(TestCase):

    services = TestCase.services + ['sanitizer']

    # NOTE: Still have to test what happens if one Item at the CommentLineItem
    #       end is removed, while the item still has references and is not
    #       removed itself.

    def test_commentline_annotated_element(self):
        """Test comment line item annotated element creation
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        # connected, but no annotated element yet
        self.assertTrue(self.get_connected(line.head) is not None)
        self.assertFalse(comment.subject.annotatedElement)


    def test_commentline_same_comment_glue(self):
        """Test comment line item glueing to already connected comment item
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        glued = self.allow(line, line.tail, comment)
        self.assertFalse(glued)


    def test_commentline_element_connect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, uml2.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        self.assertTrue(self.get_connected(line.tail) is ac)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac.subject in comment.subject.annotatedElement)


    def test_commentline_element_connect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, uml2.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        self.assertTrue(self.get_connected(line.tail) is ac)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac.subject in comment.subject.annotatedElement)


    def test_commentline_element_reconnect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, uml2.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        self.assertTrue(self.get_connected(line.tail) is ac)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac.subject in comment.subject.annotatedElement)

        ac2 = self.create(items.ActorItem, uml2.Actor)
        #ac.canvas.disconnect_item(line, line.tail)
        self.disconnect(line, line.tail)
        self.connect(line, line.tail, ac2)
        self.assertTrue(self.get_connected(line.tail) is ac2)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac2.subject in comment.subject.annotatedElement)


    def test_commentline_element_disconnect(self):
        """Test comment line connecting to comment and disconnecting actor item.
        """
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, uml2.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)

        self.assertTrue(self.get_connected(line.tail) is ac)

        self.disconnect(line, line.tail)
        self.assertFalse(self.get_connected(line.tail) is ac)

        
    def test_commentline_unlink(self):
        """Test comment line unlinking.
        """
        clazz = self.create(items.ClassItem, uml2.Class)
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, clazz)
        self.assertTrue(clazz.subject in comment.subject.annotatedElement)
        self.assertTrue(comment.subject in clazz.subject.ownedComment)

        self.assertTrue(line.canvas)

        # FixMe: This should invoke the disconnnect handler of the line's
        #  handles.

        line.unlink()

        self.assertFalse(line.canvas)
        self.assertFalse(clazz.subject in comment.subject.annotatedElement)
        self.assertFalse(comment.subject in clazz.subject.ownedComment)
        self.assertTrue(len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement)
        self.assertTrue(len(clazz.subject.ownedComment) == 0, clazz.subject.ownedComment)


    def test_commentline_element_unlink(self):
        """Test comment line unlinking using a class item.
        """
        clazz = self.create(items.ClassItem, uml2.Class)
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, clazz)
        self.assertTrue(clazz.subject in comment.subject.annotatedElement)
        self.assertTrue(comment.subject in clazz.subject.ownedComment)

        self.assertTrue(line.canvas)

        clazz_subject = clazz.subject

        # FixMe: This should invoke the disconnnect handler of the line's
        #  handles.

        clazz.unlink()

        self.assertFalse(clazz.canvas)
        self.assertTrue(line.canvas)
        self.assertFalse(comment.subject.annotatedElement)
        self.assertTrue(len(clazz_subject.ownedComment) == 0)


    def test_commentline_relationship_unlink(self):
        """Test comment line to a relationship item connection and unlink.

        Demonstrates defect #103.
        """
        clazz1 = self.create(items.ClassItem, uml2.Class)
        clazz2 = self.create(items.ClassItem, uml2.Class)
        gen = self.create(items.GeneralizationItem)

        self.connect(gen, gen.head, clazz1)
        self.connect(gen, gen.tail, clazz2)

        assert gen.subject

        # now, connect comment to a generalization (relationship)
        comment = self.create(items.CommentItem, uml2.Comment)
        line = self.create(items.CommentLineItem)
        self.connect(line, line.head, comment)
        self.connect(line, line.tail, gen)

        self.assertTrue(gen.subject in comment.subject.annotatedElement)
        self.assertTrue(comment.subject in gen.subject.ownedComment)

        # FixMe: This should invoke the disconnnect handler of the line's
        #  handles.

        gen.unlink()

        self.assertFalse(comment.subject.annotatedElement)
        self.assertTrue(gen.subject is None)


    def test_commentline_linked_to_same_element_twice(self):
        """
        It is not allowed to create two commentlines between the same elements.
        """
        clazz = self.create(items.ClassItem, uml2.Class)

        # now, connect comment to a generalization (relationship)
        comment = self.create(items.CommentItem, uml2.Comment)
        line1 = self.create(items.CommentLineItem)
        self.connect(line1, line1.head, comment)
        self.connect(line1, line1.tail, clazz)

        self.assertTrue(clazz.subject in comment.subject.annotatedElement)
        self.assertTrue(comment.subject in clazz.subject.ownedComment)

        # Now add another line

        line2 = self.create(items.CommentLineItem)
        self.connect(line2, line2.head, comment)

        self.assertFalse(self.allow(line2, line2.tail, clazz))


# vim: sw=4:et:ai
