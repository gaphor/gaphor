"""
Comment and comment line items connection adapters tests.
"""

from typing import Type, TypeVar

import pytest

from gaphor import UML
from gaphor.core.modeling import Comment
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.usecases.actor import ActorItem

T = TypeVar("T")


@pytest.fixture
def create(element_factory, diagram):
    def create(item_cls: Type[T], subject_cls=None, subject=None) -> T:
        """
        Create an item with specified subject.
        """
        if subject_cls:
            subject = element_factory.create(subject_cls)
        item = diagram.create(item_cls, subject=subject)
        diagram.canvas.update()
        return item

    return create


# NOTE: Still have to test what happens if one Item at the CommentLineItem
#       end is removed, while the item still has references and is not
#       removed itself.


def test_commentline_annotated_element(create, diagram):
    """Test comment line item annotated element creation
    """
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)

    connect(line, line.head, comment)
    # connected, but no annotated element yet
    assert diagram.canvas.get_connection(line.head)
    assert not comment.subject.annotatedElement


def test_commentline_same_comment_glue(create):
    """Test comment line item gluing to already connected comment item."""

    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)

    connect(line, line.head, comment)
    glued = allow(line, line.tail, comment)
    assert not glued


def test_commentline_element_connect(create, diagram):
    """Test comment line connecting to comment and actor items.
    """
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    ac = create(ActorItem, UML.Actor)

    connect(line, line.head, comment)
    connect(line, line.tail, ac)
    assert diagram.canvas.get_connection(line.tail).connected is ac
    assert 1 == len(comment.subject.annotatedElement)
    assert ac.subject in comment.subject.annotatedElement


def test_commentline_glie_to_item_with_no_subject(create, diagram):
    """Test comment line connecting to comment and actor items.
    """
    line = create(CommentLineItem)
    gi = create(GeneralizationItem)

    assert allow(line, line.tail, gi)


def test_commentline_item_with_no_subject_connect(create, diagram):
    """Test comment line connecting to comment and actor items.
    """
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    gi = create(GeneralizationItem)

    connect(line, line.head, comment)
    connect(line, line.tail, gi)
    assert diagram.canvas.get_connection(line.tail).connected is gi
    assert 0 == len(comment.subject.annotatedElement)


def test_commentline_element_reconnect(create, diagram):
    """Test comment line connecting to comment and actor items.
    """
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    ac = create(ActorItem, UML.Actor)

    connect(line, line.head, comment)
    connect(line, line.tail, ac)
    assert diagram.canvas.get_connection(line.tail).connected is ac
    assert 1 == len(comment.subject.annotatedElement)
    assert ac.subject in comment.subject.annotatedElement

    ac2 = create(ActorItem, UML.Actor)
    # ac.canvas.disconnect_item(line, line.tail)
    disconnect(line, line.tail)
    connect(line, line.tail, ac2)
    assert diagram.canvas.get_connection(line.tail).connected is ac2
    assert 1 == len(comment.subject.annotatedElement)
    assert ac2.subject in comment.subject.annotatedElement


def test_commentline_element_disconnect(create, diagram):
    """Test comment line connecting to comment and disconnecting actor item.
    """
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    ac = create(ActorItem, UML.Actor)

    connect(line, line.head, comment)
    connect(line, line.tail, ac)

    assert diagram.canvas.get_connection(line.tail).connected is ac

    disconnect(line, line.tail)
    assert not diagram.canvas.get_connection(line.tail)


def test_commentline_relationship_disconnect(create):
    """Test comment line to a relationship item connection and unlink.

    Demonstrates defect #103.
    """
    clazz1 = create(ClassItem, UML.Class)
    clazz2 = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem)

    connect(gen, gen.head, clazz1)
    connect(gen, gen.tail, clazz2)

    assert gen.subject

    # now, connect comment to a generalization (relationship)
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    connect(line, line.head, comment)
    connect(line, line.tail, gen)

    assert gen.subject in comment.subject.annotatedElement
    assert comment.subject in gen.subject.ownedComment

    disconnect(gen, gen.head)

    assert gen.subject is None
    assert not comment.subject.annotatedElement


def test_commentline_unlink(create):
    """Test comment line unlinking.
    """
    clazz = create(ClassItem, UML.Class)
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)

    connect(line, line.head, comment)
    connect(line, line.tail, clazz)
    assert clazz.subject in comment.subject.annotatedElement
    assert comment.subject in clazz.subject.ownedComment

    assert line.canvas

    # FixMe: This should invoke the disconnect handler of the line's
    #  handles.

    line.unlink()

    assert not line.canvas
    assert clazz.subject not in comment.subject.annotatedElement
    assert comment.subject not in clazz.subject.ownedComment
    assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
    assert len(clazz.subject.ownedComment) == 0, clazz.subject.ownedComment


def test_commentline_element_unlink(create):
    """Test comment line unlinking using a class item.
    """
    clazz = create(ClassItem, UML.Class)
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)

    connect(line, line.head, comment)
    connect(line, line.tail, clazz)
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


def test_commentline_relationship_unlink(create):
    """Test comment line to a relationship item connection and unlink.

    Demonstrates defect #103.
    """
    clazz1 = create(ClassItem, UML.Class)
    clazz2 = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem)

    connect(gen, gen.head, clazz1)
    connect(gen, gen.tail, clazz2)

    assert gen.subject

    # now, connect comment to a generalization (relationship)
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    connect(line, line.head, comment)
    connect(line, line.tail, gen)

    assert gen.subject in comment.subject.annotatedElement
    assert comment.subject in gen.subject.ownedComment

    gen.unlink()

    assert not comment.subject.annotatedElement
    assert gen.subject is None


def test_commentline_linked_to_same_element_twice(create):
    """
    It is not allowed to create two commentlines between the same elements.
    """
    clazz = create(ClassItem, UML.Class)

    # now, connect comment to a generalization (relationship)
    comment = create(CommentItem, Comment)
    line1 = create(CommentLineItem)
    connect(line1, line1.head, comment)
    connect(line1, line1.tail, clazz)

    assert clazz.subject in comment.subject.annotatedElement
    assert comment.subject in clazz.subject.ownedComment

    # Now add another line

    line2 = create(CommentLineItem)
    connect(line2, line2.head, comment)

    assert not allow(line2, line2.tail, clazz)
