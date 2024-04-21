import pytest

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.general import CommentItem, CommentLineItem
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes import ClassItem, GeneralizationItem, PackageItem
from gaphor.UML.profiles import ExtensionItem
from gaphor.UML.sanitizerservice import SanitizerService


@pytest.fixture(autouse=True)
def sanitizer(event_manager):
    sanitizer = SanitizerService(event_manager)
    yield sanitizer
    sanitizer.shutdown()


@pytest.fixture
def create_item(element_factory, diagram):
    def create(item_cls, subject_cls=None, subject=None):
        """Create an item with specified subject."""
        if subject_cls is not None:
            subject = element_factory.create(subject_cls)
        return diagram.create(item_cls, subject=subject)

    return create


def test_connect_element_with_comments(create_item, diagram):
    comment = create_item(CommentItem, Comment)
    line = create_item(CommentLineItem)
    gi = create_item(GeneralizationItem)
    clazz1 = create_item(ClassItem, UML.Class)
    clazz2 = create_item(ClassItem, UML.Class)

    connect(line, line.head, comment)
    connect(line, line.tail, gi)

    assert diagram.connections.get_connection(line.tail).connected is gi

    # Now connect generalization ends.
    connect(gi, gi.head, clazz1)
    connect(gi, gi.tail, clazz2)

    assert gi.subject in comment.subject.annotatedElement


def test_presentation_delete(create_item, element_factory):
    """Remove element if the last presentation of an item is deleted."""
    klassitem = create_item(ClassItem, UML.Class)
    klass = klassitem.subject

    assert klassitem.subject.presentation[0] is klassitem
    assert klassitem.diagram

    # Delete presentation here:

    klassitem.unlink()

    assert not klassitem.diagram
    assert klass not in element_factory


def test_no_presentation_delete_with_owned_element(create_item, element_factory):
    """Do not remove element if it has children."""
    package_item = create_item(PackageItem, UML.Package)
    package = package_item.subject
    class_item = create_item(ClassItem, UML.Class)
    klass = class_item.subject
    klass.package = package

    assert class_item.subject.presentation[0] is class_item
    assert class_item.diagram
    assert package.ownedElement[0] == klass

    # Delete presentation here:

    package_item.unlink()

    assert not package_item.diagram
    assert package in element_factory


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

    del stereotype.ownedAttribute[ext.memberEnd[0]]

    assert not klass.appliedStereotype


def test_extension_deletion(element_factory, diagram):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext = UML.recipes.create_extension(metaklass, stereotype)
    ext_item = diagram.create(ExtensionItem, subject=ext)

    # Apply stereotype to class and create slot
    instspec = UML.recipes.apply_stereotype(klass, stereotype)
    UML.recipes.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    # disconnect indirectly, by deleting the item
    ext_item.unlink()

    assert not klass.appliedStereotype


def test_extension_with_generalization_delete_extension(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    ext = UML.recipes.create_extension(metaklass, stereotype)
    substereotype = create(UML.Stereotype)
    UML.recipes.create_generalization(stereotype, substereotype)
    UML.recipes.apply_stereotype(klass, substereotype)

    ext.unlink()

    assert not klass.appliedStereotype


def test_extension_with_generalization_retain_specific_sterotype(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    UML.recipes.create_extension(metaklass, stereotype)
    ext = UML.recipes.create_extension(metaklass, stereotype)
    substereotype = create(UML.Stereotype)
    UML.recipes.create_generalization(stereotype, substereotype)
    UML.recipes.create_generalization(substereotype, stereotype)
    UML.recipes.apply_stereotype(klass, substereotype)

    ext.unlink()

    assert substereotype in klass.appliedStereotype[:].classifier


def test_extension_with_generalization_delete_generalization(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    klass = create(UML.Class)
    stereotype = create(UML.Stereotype)
    UML.recipes.create_extension(metaklass, stereotype)
    substereotype = create(UML.Stereotype)
    gen = UML.recipes.create_generalization(stereotype, substereotype)
    UML.recipes.apply_stereotype(klass, substereotype)

    gen.unlink()

    assert not klass.appliedStereotype


def test_extension_deletion_with_2_metaclasses(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    metaiface = create(UML.Class)
    metaiface.name = "Interface"
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    ext1 = UML.recipes.create_extension(metaklass, stereotype)
    UML.recipes.create_extension(metaiface, stereotype)

    # Apply stereotype to class and create slot
    klass = create(UML.Class)
    iface = create(UML.Interface)
    instspec1 = UML.recipes.apply_stereotype(klass, stereotype)
    instspec2 = UML.recipes.apply_stereotype(iface, stereotype)
    UML.recipes.add_slot(instspec1, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier
    assert klass in element_factory

    ext1.unlink()

    assert not klass.appliedStereotype
    assert klass in element_factory
    assert instspec2 in iface.appliedStereotype


def test_stereotype_deletion(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    stereotype = create(UML.Stereotype)
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr
    UML.recipes.create_extension(metaklass, stereotype)

    # Apply stereotype to class and create slot
    klass = create(UML.Class)
    instspec = UML.recipes.apply_stereotype(klass, stereotype)
    UML.recipes.add_slot(instspec, st_attr)

    assert stereotype in klass.appliedStereotype[:].classifier

    stereotype.unlink()

    assert not klass.appliedStereotype


def test_extension_generalization_with_attribute_from_super_type(element_factory):
    create = element_factory.create
    metaklass = create(UML.Class)
    metaklass.name = "Class"
    stereotype = create(UML.Stereotype)
    UML.recipes.create_extension(metaklass, stereotype)
    substereotype = create(UML.Stereotype)
    UML.recipes.create_generalization(stereotype, substereotype)

    # Add attribute to super-stereotype
    st_attr = create(UML.Property)
    stereotype.ownedAttribute = st_attr

    # Apply sub-stereotype and assign parent attribute
    klass = create(UML.Class)
    instspec = UML.recipes.apply_stereotype(klass, substereotype)
    UML.recipes.add_slot(instspec, st_attr)

    st_attr.unlink()

    assert substereotype in klass.appliedStereotype[:].classifier
    assert not klass.appliedStereotype[0].slot


def test_diagram_redraw_on_owner_change(element_factory, monkeypatch):
    diagram = element_factory.create(Diagram)
    diagram.create(CommentItem, subject=element_factory.create(Comment))

    request_update_called = 0

    def mock_request_update(item):
        nonlocal request_update_called
        request_update_called += 1

    monkeypatch.setattr(diagram, "request_update", mock_request_update)

    package = element_factory.create(UML.Package)
    diagram.element = package

    assert request_update_called
