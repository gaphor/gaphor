import pytest

from gaphor import UML
from gaphor.diagram.classes import ClassItem, GeneralizationItem
from gaphor.diagram.general import CommentItem, CommentLineItem
from gaphor.diagram.tests.fixtures import (
    connect,
    diagram,
    element_factory,
    event_manager,
)
from gaphor.services.sanitizerservice import SanitizerService
from gaphor.tests import TestCase


@pytest.fixture(autouse=True)
def sanitizer(event_manager):
    sanitizer = SanitizerService(event_manager)
    yield sanitizer
    sanitizer.shutdown()


@pytest.fixture
def create_item(element_factory, diagram):
    def create(item_cls, subject_cls=None, subject=None):
        """
        Create an item with specified subject.
        """
        if subject_cls is not None:
            subject = element_factory.create(subject_cls)
        item = diagram.create(item_cls, subject=subject)
        diagram.canvas.update()
        return item

    return create


def test_connect_element_with_comments(create_item):
    comment = create_item(CommentItem, UML.Comment)
    line = create_item(CommentLineItem)
    gi = create_item(GeneralizationItem)
    clazz1 = create_item(ClassItem, UML.Class)
    clazz2 = create_item(ClassItem, UML.Class)

    connect(line, line.head, comment)
    connect(line, line.tail, gi)

    assert line.canvas.get_connection(line.tail).connected is gi

    # Now connect generaliztion ends.
    connect(gi, gi.head, clazz1)
    connect(gi, gi.tail, clazz2)

    assert gi.subject in comment.subject.annotatedElement


def test_presentation_delete(create_item, element_factory):
    """
    Remove element if the last instance of an item is deleted.
    """
    klassitem = create_item(ClassItem, UML.Class)
    klass = klassitem.subject

    assert klassitem.subject.presentation[0] is klassitem
    assert klassitem.canvas

    # Delete presentation here:

    klassitem.unlink()

    assert not klassitem.canvas
    assert klass not in element_factory


def test_stereotype_attribute_delete(element_factory):
    """
    This test was applicable to the Sanitizer service, but is now resolved
    by a tweak in the data model (Instances diagram).
    """
    create = element_factory.create
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr

    # Apply stereotype to class and create slot
    instspec = UML.model.apply_stereotype(klass, stereotype)
    slot = UML.model.add_slot(instspec, st_attr)

    # Now, what happens if the attribute is deleted:
    assert st_attr in stereotype.ownedMember
    assert slot in instspec.slot

    st_attr.unlink()

    assert [] == list(stereotype.ownedMember)
    assert [] == list(instspec.slot)


def test_extension_disconnect(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext = UML.model.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    instspec = UML.model.apply_stereotype(klass, stereotype)
    UML.model.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    # Causes set event
    del ext.ownedEnd.type

    assert [] == list(klass.appliedStereotype)


def test_extension_deletion(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext = UML.model.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    instspec = UML.model.apply_stereotype(klass, stereotype)
    UML.model.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    ext.unlink()

    assert [] == list(klass.appliedStereotype)


def test_extension_deletion_with_2_metaclasses(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    metaiface = create(UML.Class)
    metaiface.name = "Interface"
    klass = create(UML.Class)
    iface = create(UML.Interface)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext1 = UML.model.create_extension(metaklass, stereotype)
    UML.model.create_extension(metaiface, stereotype)

    # Apply stereotype to class and create slot
    instspec1 = UML.model.apply_stereotype(klass, stereotype)
    instspec2 = UML.model.apply_stereotype(iface, stereotype)
    UML.model.add_slot(instspec1, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier
    assert klass in element_factory

    ext1.unlink()

    assert [] == list(klass.appliedStereotype)
    assert klass in element_factory
    assert [instspec2] == list(iface.appliedStereotype)


def test_stereotype_deletion(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    UML.model.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    instspec = UML.model.apply_stereotype(klass, stereotype)
    UML.model.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    stereotype.unlink()

    assert [] == list(klass.appliedStereotype)
