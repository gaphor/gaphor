from uuid import uuid1

import pytest
from gaphor.core.modeling import (
    Diagram,
    Element,
    ElementChange,
    RefChange,
    ValueChange,
)
from gaphor.ui.modelmerge.organize import organize_changes


@pytest.fixture(autouse=True)
def mock_gettext(monkeypatch):
    monkeypatch.setattr("gaphor.ui.modelmerge.organize.gettext", lambda s: s)


@pytest.fixture
def change(element_factory):
    def _change(change_type, **kwargs):
        assert "op" in kwargs
        if "element_id" not in kwargs:
            kwargs["element_id"] = str(uuid1())

        if change_type is ElementChange:
            assert "element_name" in kwargs
        elif change_type is RefChange:
            assert "property_name" in kwargs
            if "property_ref" not in kwargs:
                kwargs["property_ref"] = str(uuid1())
        elif change_type is ValueChange:
            assert "property_name" in kwargs
            assert "property_value" in kwargs

        c = element_factory.create(change_type)
        for n, v in kwargs.items():
            setattr(c, n, v)

        return c

    return _change


def test_add_element(element_factory):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Add element of type Diagram"
    assert change in add_element.elements


def test_remove_element(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "remove"
    change.element_id = diagram.id
    change.element_name = "Diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Remove element “my diagram”"
    assert change in add_element.elements


def test_add_element_with_attribute_update(element_factory):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Diagram"
    vchange: ValueChange = element_factory.create(ValueChange)
    vchange.op = "update"
    vchange.element_id = "1234"
    vchange.property_name = "name"
    vchange.property_value = "my diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Add Diagram “my diagram”"
    assert change in add_element.elements
    assert vchange in add_element.elements
    assert not add_element.children


def test_remove_element_with_attribute_update(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = diagram.id
    change.element_name = "Diagram"
    vchange: ValueChange = element_factory.create(ValueChange)
    vchange.op = "update"
    vchange.element_id = diagram.id
    vchange.property_name = "name"
    vchange.property_value = "my diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Add Diagram “my diagram”"
    assert change in add_element.elements
    assert vchange in add_element.elements
    assert not add_element.children


@pytest.mark.xfail
def test_attribute_update(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    vchange: ValueChange = element_factory.create(ValueChange)
    vchange.op = "update"
    vchange.element_id = diagram.id
    vchange.property_name = "name"
    vchange.property_value = "my diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Update element my diagram"
    assert not add_element.elements
    assert add_element.children
    assert vchange in add_element.children


@pytest.mark.xfail
def test_update_reference_without_name(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    element = element_factory.create(Element)
    vchange: RefChange = element_factory.create(RefChange)
    vchange.op = "add"
    vchange.element_id = diagram.id
    vchange.property_name = "element"
    vchange.property_ref = element.id

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Update element my diagram"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].label == "Add relation element to nameless object"


@pytest.mark.xfail
def test_update_reference_with_name(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    element = element_factory.create(Element)
    vchange: RefChange = element_factory.create(RefChange)
    vchange.op = "add"
    vchange.element_id = element.id
    vchange.property_name = "diagram"
    vchange.property_ref = diagram.id

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Update element of type Element"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].label == "Add relation diagram to my diagram"


@pytest.mark.xfail
def test_remove_reference_with_name(element_factory):
    diagram = element_factory.create(Diagram)
    diagram.name = "my diagram"
    element = element_factory.create(Element)
    vchange: RefChange = element_factory.create(RefChange)
    vchange.op = "remove"
    vchange.element_id = element.id
    vchange.property_name = "diagram"
    vchange.property_ref = diagram.id

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.label == "Update element of type Element"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].label == "Remove relation diagram to my diagram"


def test_add_diagram_with_reference(element_factory, change):
    add_diagram = change(ElementChange, op="add", element_name="Diagram")
    ref = change(
        RefChange,
        op="add",
        element_id=add_diagram.element_id,
        property_name="package",
    )

    tree = list(organize_changes(element_factory))

    assert add_diagram in tree[0].elements
    assert tree[0].children
    assert ref in tree[0].children[0].elements


def test_add_diagram_contains_presentation(element_factory, change):
    add_diagram = change(ElementChange, op="add", element_name="Diagram")
    add_class_item = change(ElementChange, op="add", element_name="ClassItem")
    change(
        RefChange,
        op="add",
        element_id=add_diagram.element_id,
        property_name="ownedPresentation",
        property_ref=add_class_item.element_id,
    )

    tree = list(organize_changes(element_factory))

    assert add_diagram in tree[0].elements
    assert tree[0].children
    assert add_class_item in tree[0].children[0].elements


def test_add_diagram_contains_presentation_with_subject(element_factory, change):
    add_diagram = change(ElementChange, op="add", element_name="Diagram")
    add_class_item = change(ElementChange, op="add", element_name="ClassItem")
    change(
        RefChange,
        op="add",
        element_id=add_diagram.element_id,
        property_name="ownedPresentation",
        property_ref=add_class_item.element_id,
    )
    add_class = change(ElementChange, op="add", element_name="Class")
    change(
        RefChange,
        op="add",
        element_id=add_class_item.element_id,
        property_name="subject",
        property_ref=add_class.element_id,
    )

    tree = list(organize_changes(element_factory))

    assert add_diagram in tree[0].elements
    assert tree[0].children
    assert add_class_item in tree[0].children[0].elements
    assert tree[0].children[0].children
    assert add_class in tree[0].children[0].children[0].elements
