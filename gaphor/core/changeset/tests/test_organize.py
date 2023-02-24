from gaphor.core.modeling import (
    Diagram,
    Element,
    ElementChange,
    RefChange,
    ValueChange,
)
from gaphor.core.changeset.organize import organize_changes


def test_add_element(element_factory):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Diagram"

    tree = list(organize_changes(element_factory))

    add_element = tree[0]

    assert len(tree) == 1
    assert add_element.text == "Add element of type Diagram"
    assert add_element.element is change


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
    assert add_element.text == "Remove element my diagram"
    assert add_element.element is change


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
    assert add_element.text == "Add element of type Diagram"
    assert add_element.element is change
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Update attribute name to my diagram"


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
    assert add_element.text == "Add element of type Diagram"
    assert add_element.element is change
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Update attribute name to my diagram"


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
    assert add_element.text == "Update element my diagram"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Update attribute name to my diagram"


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
    assert add_element.text == "Update element my diagram"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Add relation element to <None>"


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
    assert add_element.text == "Update element of type Element"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Add relation diagram to my diagram"


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
    assert add_element.text == "Update element of type Element"
    assert add_element.element is None
    assert add_element.children
    assert add_element.children[0].element is vchange
    assert add_element.children[0].text == "Remove relation diagram to my diagram"
