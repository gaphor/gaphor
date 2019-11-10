"""
Comment and comment line items connection adapters tests.
"""

from gaphor import UML
from gaphor.diagram.classes.generalization import GeneralizationItem
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.usecases.actor import ActorItem
from gaphor.tests import TestCase


class CommentLineTestCase(TestCase):

    services = TestCase.services + ["sanitizer"]

    # NOTE: Still have to test what happens if one Item at the CommentLineItem
    #       end is removed, while the item still has references and is not
    #       removed itself.

    def test_commentline_annotated_element(self):
        """Test comment line item annotated element creation
        """
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)

        self.connect(line, line.head, comment)
        # connected, but no annotated element yet
        self.assertTrue(self.get_connected(line.head) is not None)
        assert not comment.subject.annotatedElement

    def test_commentline_same_comment_glue(self):
        """Test comment line item gluing to already connected comment item."""

        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)

        self.connect(line, line.head, comment)
        glued = self.allow(line, line.tail, comment)
        assert not glued

    def test_commentline_element_connect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)
        ac = self.create(ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        assert self.get_connected(line.tail) is ac
        assert 1 == len(comment.subject.annotatedElement)
        assert ac.subject in comment.subject.annotatedElement

    def test_commentline_element_reconnect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)
        ac = self.create(ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        assert self.get_connected(line.tail) is ac
        assert 1 == len(comment.subject.annotatedElement)
        assert ac.subject in comment.subject.annotatedElement

        ac2 = self.create(ActorItem, UML.Actor)
        # ac.canvas.disconnect_item(line, line.tail)
        self.disconnect(line, line.tail)
        self.connect(line, line.tail, ac2)
        assert self.get_connected(line.tail) is ac2
        assert 1 == len(comment.subject.annotatedElement)
        assert ac2.subject in comment.subject.annotatedElement

    def test_commentline_element_disconnect(self):
        """Test comment line connecting to comment and disconnecting actor item.
        """
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)
        ac = self.create(ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)

        assert self.get_connected(line.tail) is ac

        self.disconnect(line, line.tail)
        assert not self.get_connected(line.tail) is ac

    def test_commentline_unlink(self):
        """Test comment line unlinking.
        """
        clazz = self.create(ClassItem, UML.Class)
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, clazz)
        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        assert line.canvas

        # FixMe: This should invoke the disconnect handler of the line's
        #  handles.

        line.unlink()

        assert not line.canvas
        assert clazz.subject not in comment.subject.annotatedElement
        assert comment.subject not in clazz.subject.ownedComment
        assert (
            len(comment.subject.annotatedElement) == 0
        ), comment.subject.annotatedElement
        assert len(clazz.subject.ownedComment) == 0, clazz.subject.ownedComment

    def test_commentline_element_unlink(self):
        """Test comment line unlinking using a class item.
        """
        clazz = self.create(ClassItem, UML.Class)
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, clazz)
        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        assert line.canvas

        clazz_subject = clazz.subject

        # FixMe: This should invoke the disconnect handler of the line's
        #  handles.

        clazz.unlink()

        assert not clazz.canvas
        assert line.canvas
        assert not comment.subject.annotatedElement
        assert len(clazz_subject.ownedComment) == 0

    def test_commentline_relationship_unlink(self):
        """Test comment line to a relationship item connection and unlink.

        Demonstrates defect #103.
        """
        clazz1 = self.create(ClassItem, UML.Class)
        clazz2 = self.create(ClassItem, UML.Class)
        gen = self.create(GeneralizationItem)

        self.connect(gen, gen.head, clazz1)
        self.connect(gen, gen.tail, clazz2)

        assert gen.subject

        # now, connect comment to a generalization (relationship)
        comment = self.create(CommentItem, UML.Comment)
        line = self.create(CommentLineItem)
        self.connect(line, line.head, comment)
        self.connect(line, line.tail, gen)

        assert gen.subject in comment.subject.annotatedElement
        assert comment.subject in gen.subject.ownedComment

        gen.unlink()

        assert not comment.subject.annotatedElement
        assert gen.subject is None

    def test_commentline_linked_to_same_element_twice(self):
        """
        It is not allowed to create two commentlines between the same elements.
        """
        clazz = self.create(ClassItem, UML.Class)

        # now, connect comment to a generalization (relationship)
        comment = self.create(CommentItem, UML.Comment)
        line1 = self.create(CommentLineItem)
        self.connect(line1, line1.head, comment)
        self.connect(line1, line1.tail, clazz)

        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        # Now add another line

        line2 = self.create(CommentLineItem)
        self.connect(line2, line2.head, comment)

        assert not self.allow(line2, line2.tail, clazz)


# vim: sw=4:et:ai
