"""
Comment and comment line items connection adapters tests.
"""

from gaphor.tests import TestCase

class CommentLineTestCase(TestCase):
    def test_commentline_element(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        actor = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)

        # connect the comment item to the head of the line
        self.connect(line, line.head, comment)
        self.assertTrue(line.head.connected_to is not None)
        self.assertTrue(comment.subject.annotatedElement is None)

        # Connecting two ends of the line to the same item is not allowed:
        handle = line.tail
        adapter.connect(handle, comment.ports()[0])

        assert handle.connected_to is None, handle.connected_to
        #assert not hasattr(handle,'connection_constraint')
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the actor

        adapter = component.queryMultiAdapter((actor, line), IConnect)

        handle = line.handles()[-1]
        adapter.connect(handle, actor.ports()[0])

        assert handle.connected_to is actor
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Same thing with another actor
        # (should disconnect the already connected actor):

        handle = line.tail
        adapter = component.queryMultiAdapter((actor2, line), IConnect)
        adapter.connect(handle, actor2.ports()[0])

        assert handle.connected_to is actor2
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect actor:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle.connection_data is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.head
        adapter.disconnect(handle)
        

    def test_commentline_class(self):
        """
        Connect a CommentLine to a class and unlink the commentLine
        afterwards.
        """
        clazz = self.create(items.ClassItem, UML.Class)
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle, comment.ports()[0])

        adapter = component.queryMultiAdapter((clazz, line), IConnect)
        handle = line.tail
        adapter.connect(handle, clazz.ports()[0])

        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        line.unlink()

        assert not comment.subject.annotatedElement
        assert not clazz.subject.ownedComment


    def test_commentline_relationship_unlink(self):
        """
        Connect a CommentLine to a relationship item.
        Removing the relationship should work.

        Demonstrates defect #103.
        """
        clazz1 = self.create(items.ClassItem, UML.Class)
        clazz2 = self.create(items.ClassItem, UML.Class)
        gen = self.create(items.GeneralizationItem)

        adapter = component.queryMultiAdapter((clazz1, gen), IConnect)
        handle = gen.head
        adapter.connect(handle, clazz1.ports()[0])

        adapter = component.queryMultiAdapter((clazz2, gen), IConnect)
        handle = gen.tail
        adapter.connect(handle, clazz2.ports()[0])

        assert gen.subject

        # And now the comment:

        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((gen, line), IConnect)
        handle = line.tail
        adapter.connect(handle)

        assert gen.subject in comment.subject.annotatedElement
        assert comment.subject in gen.subject.ownedComment

        gen.unlink()

        assert not comment.subject.annotatedElement
        assert not gen.subject


    def test_commentline_association(self):
        """
        Test CommentLineItem with AssociationItem.

        # TODO: check behaviour if:
          1. comment line is connected to association + comment and after that
             association is connected to two classes.
             -> association should be connected to comment.annotatedElement
          2. association is disconnected while a comment is connected:
             -> association should be removed from comment.annotatedElement
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        assoc = self.create(items.AssociationItem)

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle, c1.ports()[0])

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle, c2.ports()[0]) 
        assert assoc.head.connected_to is c1
        assert assoc.tail.connected_to is c2
        assert assoc.subject

        # Connect the association item to the head of the line:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        assert adapter
        import gaphor.adapters.connectors
        assert type(adapter) is gaphor.adapters.connectors.CommentLineLineConnect
        handle = line.head
        pos = adapter.glue(handle)
        assert pos == (10, 50), pos
        adapter.connect(handle, assoc.ports()[0])

        assert handle.connected_to is assoc
        assert handle.connection_data is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is None
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is comment
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect comment:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle.connection_data is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Connect again:

        adapter.connect(handle)
        assert handle.connected_to is not None, handle.connected_to
