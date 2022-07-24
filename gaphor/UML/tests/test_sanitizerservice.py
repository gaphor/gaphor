import pytest

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.general import CommentItem, CommentLineItem
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes import ClassItem, GeneralizationItem
from gaphor.UML.sanitizerservice import SanitizerService


class MockUndoManager:
    def in_undo_transaction(self):
        return False


@pytest.fixture(autouse=True)
def sanitizer(event_manager):
    sanitizer = SanitizerService(event_manager, MockUndoManager())
    yield sanitizer
    sanitizer.shutdown()


def test_connect_element_with_comments(create, diagram):
    comment = create(CommentItem, Comment)
    line = create(CommentLineItem)
    gi = create(GeneralizationItem)
    clazz1 = create(ClassItem, UML.Class)
    clazz2 = create(ClassItem, UML.Class)

    connect(line, line.head, comment)
    connect(line, line.tail, gi)

    assert diagram.connections.get_connection(line.tail).connected is gi

    # Now connect generalization ends.
    connect(gi, gi.head, clazz1)
    connect(gi, gi.tail, clazz2)

    assert gi.subject in comment.subject.annotatedElement


def test_presentation_delete(create, element_factory):
    """Remove element if the last instance of an item is deleted."""
    klassitem = create(ClassItem, UML.Class)
    klass = klassitem.subject

    assert klassitem.subject.presentation[0] is klassitem
    assert klassitem.diagram

    # Delete presentation here:

    klassitem.unlink()

    assert not klassitem.diagram
    assert klass not in element_factory


def test_stereotype_attribute_delete(element_factory):
    """This test was applicable to the Sanitizer service, but is now resolved
    by a tweak in the data model (Instances diagram)."""
    create = element_factory.create
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr

    # Apply stereotype to class and create slot
    instspec = UML.recipes.apply_stereotype(klass, stereotype)
    slot = UML.recipes.add_slot(instspec, st_attr)

    # Now, what happens if the attribute is deleted:
    assert st_attr in stereotype.ownedMember
    assert slot in instspec.slot

    st_attr.unlink()

    assert not stereotype.ownedMember
    assert not instspec.slot


def test_extension_disconnect(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext = UML.recipes.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    instspec = UML.recipes.apply_stereotype(klass, stereotype)
    UML.recipes.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    # Causes set event
    del ext.ownedEnd.type

    assert klass.appliedStereotype


def test_stereotype_deletion(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    UML.recipes.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    instspec = UML.recipes.apply_stereotype(klass, stereotype)
    UML.recipes.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    stereotype.unlink()

    assert not klass.appliedStereotype


def test_diagram_move(element_factory, mocker):
    diagram = element_factory.create(Diagram)
    diagram.create(CommentItem, subject=element_factory.create(Comment))
    mocked_func = mocker.patch.object(diagram, "request_update")

    package = element_factory.create(UML.Package)
    diagram.element = package

    mocked_func.assert_called()
