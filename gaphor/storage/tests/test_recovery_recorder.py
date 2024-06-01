import pytest
from gaphas.segment import Segment

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram, ElementFactory
from gaphor.diagram.general import CommentItem, Line
from gaphor.diagram.tests.fixtures import connect, disconnect
from gaphor.storage.recovery import Recorder, replay_events
from gaphor.UML.diagramitems import ClassItem, DependencyItem


@pytest.fixture
def recorder(event_manager):
    recorder = Recorder()
    recorder.subscribe(event_manager)
    yield recorder
    recorder.unsubscribe(event_manager)


def test_record_create_element(
    recorder, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)

    new_model = ElementFactory(event_manager)

    replay_events(recorder.events[:], new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recorder.events
    assert new_model.lookup(comment.id)


def test_record_create_presentation(
    recorder, event_manager, diagram, modeling_language
):
    comment = diagram.create(CommentItem)

    new_model = ElementFactory(event_manager)
    new_model.create_as(Diagram, id=diagram.id)

    replay_events(recorder.events[:], new_model, modeling_language)

    assert ("c", "CommentItem", comment.id, diagram.id) in recorder.events

    assert new_model.lookup(comment.id)


def test_record_delete_element(
    recorder, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    comment.unlink()

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recorder.events
    assert ("u", comment.id, None) in recorder.events
    assert not new_model.lookup(comment.id)


def test_record_delete_presentation(
    recorder, event_manager, diagram, modeling_language
):
    comment = diagram.create(CommentItem)
    comment.unlink()

    new_model = ElementFactory(event_manager)
    new_model.create_as(Diagram, diagram.id)
    replay_events(recorder.events[:], new_model, modeling_language)

    assert ("c", "CommentItem", comment.id, diagram.id) in recorder.events
    assert ("u", comment.id, diagram.id) in recorder.events
    assert not new_model.lookup(comment.id)


def test_record_update_attribute(
    recorder, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    comment.body = "Foo"

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    assert ("c", "Comment", comment.id, None) in recorder.events
    assert ("a", comment.id, "body", "Foo") in recorder.events
    assert new_model.lookup(comment.id)
    assert new_model.lookup(comment.id).body == "Foo"


def test_record_set_association(
    recorder, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    diagram = element_factory.create(Diagram)
    diagram.element = comment

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_comment = new_model.lookup(comment.id)
    new_diagram = new_model.lookup(diagram.id)

    assert ("s", diagram.id, "element", comment.id) in recorder.events
    assert ("s", comment.id, "ownedDiagram", diagram.id) in recorder.events

    assert new_comment is new_diagram.element
    assert new_diagram in new_comment.ownedDiagram


def test_record_delete_association(
    recorder, event_manager, element_factory, modeling_language
):
    comment = element_factory.create(Comment)
    diagram = element_factory.create(Diagram)
    diagram.element = comment
    del diagram.element

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_comment = new_model.lookup(comment.id)
    new_diagram = new_model.lookup(diagram.id)

    assert ("s", diagram.id, "element", None) in recorder.events
    assert ("d", comment.id, "ownedDiagram", diagram.id) in recorder.events

    assert not new_diagram.element
    assert new_diagram not in new_comment.ownedDiagram


def test_record_move_element(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    class_item.matrix.translate(200, 100)

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_class_item = new_model.lookup(class_item.id)

    assert new_class_item.matrix[4] == pytest.approx(200)
    assert new_class_item.matrix[5] == pytest.approx(100)


def test_record_move_handle_element(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    class_item.handles()[2].pos = (200, 100)

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_class_item = new_model.lookup(class_item.id)

    assert new_class_item.handles()[2].pos.x == 200
    assert new_class_item.handles()[2].pos.y == 100


def test_record_connect_element(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    dependency_item = diagram.create(DependencyItem)
    connect(dependency_item, dependency_item.head, class_item)

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_diagram = new_model.lookup(diagram.id)
    new_class_item = new_model.lookup(class_item.id)
    new_dependency_item = new_model.lookup(dependency_item.id)
    cinfo = new_diagram.connections.get_connection(new_dependency_item.head)

    assert cinfo
    assert cinfo.item is new_dependency_item
    assert cinfo.connected is new_class_item


def test_record_connect_both_ends(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    other_class_item = diagram.create(
        ClassItem, subject=element_factory.create(UML.Class)
    )
    dependency_item = diagram.create(DependencyItem)
    connect(dependency_item, dependency_item.head, class_item)
    connect(dependency_item, dependency_item.tail, other_class_item)

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_diagram = new_model.lookup(diagram.id)
    new_class_item = new_model.lookup(class_item.id)
    new_other_class_item = new_model.lookup(other_class_item.id)
    new_dependency_item = new_model.lookup(dependency_item.id)
    cinfo_head = new_diagram.connections.get_connection(new_dependency_item.head)
    cinfo_tail = new_diagram.connections.get_connection(new_dependency_item.tail)

    assert new_dependency_item.subject
    assert new_dependency_item.subject.supplier is new_class_item.subject
    assert new_dependency_item.subject.client is new_other_class_item.subject
    assert cinfo_head
    assert cinfo_tail
    assert cinfo_head.item is new_dependency_item
    assert cinfo_head.connected is new_class_item


def test_record_disconnect_element(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    other_class_item = diagram.create(
        ClassItem, subject=element_factory.create(UML.Class)
    )
    dependency_item = diagram.create(DependencyItem)
    connect(dependency_item, dependency_item.head, class_item)
    connect(dependency_item, dependency_item.tail, other_class_item)
    disconnect(dependency_item, dependency_item.tail)

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_diagram = new_model.lookup(diagram.id)
    new_class_item = new_model.lookup(class_item.id)
    new_dependency_item = new_model.lookup(dependency_item.id)
    cinfo_head = new_diagram.connections.get_connection(new_dependency_item.head)
    cinfo_tail = new_diagram.connections.get_connection(new_dependency_item.tail)

    assert cinfo_head
    assert cinfo_head.item is new_dependency_item
    assert cinfo_head.connected is new_class_item
    assert not cinfo_tail


def test_record_reconnect_element(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    class_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    dependency_item = diagram.create(DependencyItem)
    connect(dependency_item, dependency_item.head, class_item)
    dependency_item.head.pos = (100, 100)
    connect(dependency_item, dependency_item.head, class_item)
    diagram.update()

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_diagram = new_model.lookup(diagram.id)
    new_dependency_item = new_model.lookup(dependency_item.id)
    new_diagram.update()

    assert ("ir", dependency_item.id, 0, class_item.id, 1) in recorder.events
    assert dependency_item.head.pos == new_dependency_item.head.pos


def test_record_split_line_segments(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    line_item = diagram.create(Line)
    Segment(line_item, diagram).split_segment(0, 2)
    handle_positions = [tuple(h.pos) for h in line_item.handles()]

    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    new_line_item = new_model.lookup(line_item.id)
    new_handle_positions = [tuple(h.pos) for h in new_line_item.handles()]

    assert len(new_handle_positions) == 3
    assert handle_positions == new_handle_positions


def test_record_merge_line_segments(
    recorder, event_manager, element_factory, modeling_language
):
    diagram = element_factory.create(Diagram)
    line_item = diagram.create(Line)
    Segment(line_item, diagram).split_segment(0, 3)
    new_model = ElementFactory(event_manager)
    replay_events(recorder.events[:], new_model, modeling_language)

    recorder.truncate()
    Segment(line_item, diagram).merge_segment(1, 2)
    handle_positions = [tuple(h.pos) for h in line_item.handles()]
    replay_events(recorder.events[:], new_model, modeling_language)

    new_line_item = new_model.lookup(line_item.id)
    new_handle_positions = [tuple(h.pos) for h in new_line_item.handles()]

    assert len(new_handle_positions) == 3
    assert handle_positions == new_handle_positions
