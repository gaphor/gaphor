"""Unittest the storage and parser modules."""

import re
from io import StringIO

import pytest

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram, StyleSheet
from gaphor.diagram.general import CommentItem
from gaphor.diagram.tests.fixtures import connect
from gaphor.storage import storage
from gaphor.UML.classes import AssociationItem, ClassItem, InterfaceItem


class PseudoFile:
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def close(self):
        pass


def test_version_check():
    from gaphor.storage.storage import version_lower_than

    assert version_lower_than("0.3.0", (0, 15, 0))
    assert version_lower_than("0", (0, 15, 0))
    assert version_lower_than("0.14", (0, 15, 0))
    assert version_lower_than("0.14.1111", (0, 15, 0))
    assert not version_lower_than("0.15.0", (0, 15, 0))
    assert not version_lower_than("1.33.0", (0, 15, 0))
    assert not version_lower_than("0.15.0b123", (0, 15, 0))
    assert version_lower_than("0.14.0.b1", (0, 15, 0))
    assert not version_lower_than("0.15.b1", (0, 15, 0))
    assert not version_lower_than("0.16.b1", (0, 15, 0))
    assert not version_lower_than("0.15.0.b2", (0, 14, 99))
    assert not version_lower_than("1.2.0rc2-dev0+7fad31a0", (0, 17, 0))


def test_save_uml(element_factory):
    """Saving gaphor.UML model elements."""
    element_factory.create(UML.Package)
    element_factory.create(Diagram)
    element_factory.create(Comment)
    element_factory.create(UML.Class)

    out = PseudoFile()
    storage.save(out, element_factory=element_factory)
    out.close()

    assert "<Package " in out.data
    assert "<Diagram " in out.data
    assert "<Comment " in out.data
    assert "<Class " in out.data


def test_save_item(diagram, element_factory):
    """Save a diagram item too."""
    diagram = element_factory.create(Diagram)
    diagram.create(CommentItem, subject=element_factory.create(Comment))

    out = PseudoFile()
    storage.save(out, element_factory=element_factory)
    out.close()

    assert "<Diagram " in out.data
    assert "<Comment " in out.data
    assert "<canvas>" not in out.data
    assert "<CommentItem " in out.data, out.data


def test_load_uml(element_factory, saver, loader):
    """Test loading of a freshly saved model."""
    element_factory.create(UML.Package)
    # diagram is created in case's init
    element_factory.create(Comment)
    element_factory.create(UML.Class)

    data = saver()
    loader(data)

    assert len(element_factory.lselect()) == 4
    assert len(element_factory.lselect(UML.Package)) == 1
    assert len(element_factory.lselect(Comment)) == 1
    assert len(element_factory.lselect(UML.Class)) == 1
    assert len(element_factory.lselect(StyleSheet)) == 1


def test_load_uml_2(create, element_factory, saver, loader):
    """Test loading of a freshly saved model."""
    element_factory.create(UML.Package)
    create(CommentItem, Comment)
    create(ClassItem, UML.Class)
    iface = create(InterfaceItem, UML.Interface)
    iface.subject.name = "Circus"
    iface.matrix.translate(10, 10)

    data = saver()
    loader(data)

    assert len(element_factory.lselect()) == 9
    assert len(element_factory.lselect(UML.Package)) == 1
    assert len(element_factory.lselect(Diagram)) == 1
    d = element_factory.lselect(Diagram)[0]
    assert len(element_factory.lselect(Comment)) == 1
    assert len(element_factory.lselect(UML.Class)) == 1
    assert len(element_factory.lselect(UML.Interface)) == 1

    c = element_factory.lselect(UML.Class)[0]
    assert c.presentation
    assert c.presentation[0].subject is c

    iface = element_factory.lselect(UML.Interface)[0]
    assert iface.name == "Circus"
    assert len(iface.presentation) == 1
    assert tuple(iface.presentation[0].matrix) == (1, 0, 0, 1, 10, 10), tuple(
        iface.presentation[0].matrix
    )

    # Check load/save of other canvas items.
    assert len(list(d.get_all_items())) == 3
    for item in d.get_all_items():
        assert item.subject, f"No subject for {item}"
    d1 = next(d.select(lambda e: isinstance(e, ClassItem)))
    assert d1


def test_load_with_whitespace_name(diagram, element_factory, saver, loader):
    difficult_name = "    with space before and after  "
    diagram = element_factory.lselect()[0]
    diagram.name = difficult_name
    data = saver()
    loader(data)
    elements = element_factory.lselect()
    assert len(elements) == 2, elements
    assert elements[0].name == difficult_name, elements[0].name


def test_save_and_load_model_with_relationships(
    create, diagram, element_factory, saver, loader
):
    element_factory.create(UML.Package)
    create(CommentItem, Comment)
    create(ClassItem, UML.Class)

    a = diagram.create(AssociationItem)
    a.handles()[0].pos = (10, 20)
    a.handles()[1].pos = (50, 60)
    assert a.handles()[0].pos.x == 10, a.handles()[0].pos
    assert a.handles()[0].pos.y == 20, a.handles()[0].pos
    assert tuple(a.handles()[1].pos) == (50, 60), a.handles()[1].pos

    data = saver()
    loader(data)

    assert len(element_factory.lselect()) == 8
    assert len(element_factory.lselect(UML.Package)) == 1
    assert len(element_factory.lselect(Diagram)) == 1
    d = element_factory.lselect(Diagram)[0]
    assert len(element_factory.lselect(Comment)) == 1
    assert len(element_factory.lselect(UML.Class)) == 1
    assert len(element_factory.lselect(UML.Association)) == 0

    # Check load/save of other canvas items.
    assert len(list(d.get_all_items())) == 3
    aa = next(item for item in d.get_all_items() if isinstance(item, AssociationItem))
    assert aa
    assert list(map(float, aa.handles()[0].pos)) == [10, 20], aa.handles()[0].pos
    assert list(map(float, aa.handles()[1].pos)) == [50, 60], aa.handles()[1].pos
    d1 = next(d.select(lambda e: isinstance(e, ClassItem)))
    assert d1


def test_save_and_load_of_association_with_two_connected_classes(
    create, diagram, element_factory, modeling_language
):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    c2.matrix.translate(200, 200)
    diagram.request_update(c2)
    diagram.update({c1, c2})
    assert tuple(c2.matrix_i2c) == (1, 0, 0, 1, 200, 200)

    a = create(AssociationItem)

    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    diagram.update({c1, c2, a})

    assert a.head.pos.y == 0, a.head.pos
    assert a.tail.pos.x == 200, a.tail.pos
    assert a.tail.pos.y == 200, a.tail.pos
    assert a.subject

    fd = StringIO()
    storage.save(fd, element_factory=element_factory)
    data = fd.getvalue()
    fd.close()

    old_a_subject_id = a.subject.id

    element_factory.flush()
    assert not list(element_factory.select())
    fd = StringIO(data)
    storage.load(
        fd, element_factory=element_factory, modeling_language=modeling_language
    )
    fd.close()

    diagrams = element_factory.lselect(Diagram)
    assert len(diagrams) == 1
    d = diagrams[0]
    a = next(d.select(lambda e: isinstance(e, AssociationItem)))
    assert a.subject is not None
    assert old_a_subject_id == a.subject.id
    cinfo_head = a.diagram.connections.get_connection(a.head)
    assert cinfo_head.connected is not None
    cinfo_tail = a.diagram.connections.get_connection(a.tail)
    assert cinfo_tail.connected is not None
    assert cinfo_head.connected is not cinfo_tail.connected


def test_load_and_save_of_a_model(element_factory, modeling_language, test_models):
    path = test_models / "simple-items.gaphor"

    with open(path, encoding="utf-8") as ifile:
        storage.load(
            ifile,
            element_factory=element_factory,
            modeling_language=modeling_language,
        )

    pf = PseudoFile()

    storage.save(pf, element_factory=element_factory)

    orig = path.read_text(encoding="utf-8")
    copy = pf.data

    expr = re.compile('gaphor-version="[^"]*"')
    orig = expr.sub("%VER%", orig)
    copy = expr.sub("%VER%", copy)

    assert copy == orig, "Saved model does not match copy"


def test_can_not_load_models_older_that_0_17_0(
    element_factory, modeling_language, test_models
):
    path = test_models / "old-gaphor-version.gaphor"

    def load_old_model():
        with open(path, encoding="utf-8") as ifile:
            storage.load(
                ifile,
                element_factory=element_factory,
                modeling_language=modeling_language,
            )

    with pytest.raises(ValueError):
        load_old_model()


def test_save_with_invalid_collection(element_factory, saver, caplog):
    c = element_factory.create(UML.Class)

    p = UML.Package()
    c.package = p
    data = saver()

    assert c.id in data
    assert p.id not in data
    assert "Model has unknown reference" in caplog.text


def test_save_with_invalidreference(element_factory, saver, caplog):
    p = element_factory.create(UML.Package)

    c = UML.Class()
    c.package = p
    data = saver()

    assert p.id in data
    assert c.id not in data
    assert "Model has unknown reference" in caplog.text


def test_save_and_load_with_invalid_element_type(element_factory, saver, loader):
    element_factory.create(UML.Package)

    data = saver()
    data = data.replace("Package", "Foobar")

    with pytest.raises(storage.UnknownModelElementError):
        loader(data)


def test_save_and_load_with_invalid_attribute(element_factory, saver, loader):
    p = element_factory.create(UML.Package)
    p.name = "name"

    data = saver()
    data = data.replace("name", "foobar")
    loader(data)

    package = next(element_factory.select(UML.Package))

    assert not hasattr(package, "foobar")
    assert not package.name


def test_save_and_load_with_invalid_reference(element_factory, saver, loader):
    p1 = element_factory.create(UML.Package)
    p2 = element_factory.create(UML.Package)
    p2.package = p1

    data = saver()
    data = data.replace(p1.id, "foobar", 1)
    loader(data)

    package = next(element_factory.select(UML.Package))

    assert not hasattr(package, "foobar")
    assert not package.name
