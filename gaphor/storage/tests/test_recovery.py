import pytest

from gaphor.core.modeling import Comment, Diagram, ElementFactory
from gaphor.diagram.general import CommentItem
from gaphor.storage.recovery import Recovery


@pytest.fixture
def recovery(event_manager, element_factory):
    recovery = Recovery(event_manager, element_factory)
    yield recovery
    recovery.shutdown()


def test_initialize(event_manager, element_factory):
    assert recovery


def test_record_create_element(
    recovery, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)

    new_model = ElementFactory(event_manager)

    recovery.replay(new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recovery.events
    assert new_model.lookup(comment.id)


def test_record_create_presentation(
    recovery, event_manager, diagram, modeling_language
):
    comment = diagram.create(CommentItem)

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    assert ("c", "CommentItem", comment.id, diagram.id) in recovery.events

    assert new_model.lookup(comment.id)


def test_record_delete_element(
    recovery, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    comment.unlink()

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recovery.events
    assert ("u", comment.id, None) in recovery.events
    assert not new_model.lookup(comment.id)


def test_record_delete_presentation(
    recovery, event_manager, diagram, modeling_language
):
    comment = diagram.create(CommentItem)
    comment.unlink()

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    assert ("c", "CommentItem", comment.id, diagram.id) in recovery.events
    assert ("u", comment.id, diagram.id) in recovery.events
    assert not new_model.lookup(comment.id)


def test_record_update_attribute(
    recovery, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    comment.body = "Foo"

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recovery.events
    assert ("a", comment.id, "body", "Foo") in recovery.events
    assert new_model.lookup(comment.id)
    assert new_model.lookup(comment.id).body == "Foo"


def test_record_set_association(
    recovery, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    diagram = element_factory.create(Diagram)
    diagram.element = comment

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    new_comment = new_model.lookup(comment.id)
    new_diagram = new_model.lookup(diagram.id)

    assert ("s", diagram.id, "element", comment.id) in recovery.events
    assert ("s", comment.id, "ownedDiagram", diagram.id) in recovery.events

    assert new_comment is new_diagram.element
    assert new_diagram in new_comment.ownedDiagram


def test_record_delete_association(
    recovery, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    diagram = element_factory.create(Diagram)
    diagram.element = comment
    del diagram.element

    new_model = ElementFactory(event_manager)
    recovery.replay(new_model, modeling_language)

    new_comment = new_model.lookup(comment.id)
    new_diagram = new_model.lookup(diagram.id)

    assert ("s", diagram.id, "element", None) in recovery.events
    assert ("d", comment.id, "ownedDiagram", diagram.id) in recovery.events

    assert not new_diagram.element
    assert new_diagram not in new_comment.ownedDiagram
