"""
Comment and comment line items connection adapters tests.
"""

from gaphor import UML
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
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        # connected, but no annotated element yet
        self.assertTrue(line.head.connected_to is not None)
        self.assertFalse(comment.subject.annotatedElement)


    def test_commentline_same_comment_glue(self):
        """Test comment line item glueing to already connected comment item
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        glued = self.glue(line, line.tail, comment)
        self.assertFalse(glued)


    def test_commentline_element_connect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        self.assertTrue(line.tail.connected_to is ac)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac.subject in comment.subject.annotatedElement)


    def test_commentline_element_disconnect(self):
        """Test comment line connecting to comment and disconnecting actor item.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)

        assert line.tail.connected_to is ac

        self.disconnect(line, line.tail)
        self.assertFalse(line.tail.connected_to is ac)

        
    def test_commentline_unlink(self):
        """Test comment line unlinking.
        """
        clazz = self.create(items.ClassItem, UML.Class)
        comment = self.create(items.CommentItem, UML.Comment)
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
        clazz = self.create(items.ClassItem, UML.Class)
        comment = self.create(items.CommentItem, UML.Comment)
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
        clazz1 = self.create(items.ClassItem, UML.Class)
        clazz2 = self.create(items.ClassItem, UML.Class)
        gen = self.create(items.GeneralizationItem)

        self.connect(gen, gen.head, clazz1)
        self.connect(gen, gen.tail, clazz2)

        assert gen.subject

        # now, connect comment to a generalization (relationship)
        comment = self.create(items.CommentItem, UML.Comment)
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


# vim: sw=4:et:ai
