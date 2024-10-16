import pytest

from gaphor.storage.parser import element
from gaphor.storage.storage import load_elements
from gaphor.storage.upgrade_canvasitem import upgrade_canvasitem
from gaphor.UML import diagramitems


@pytest.fixture
def loader(element_factory, modeling_language):
    def _loader(*parsed_items):
        for item in parsed_items:
            if item.type.endswith("Item"):
                item.references["diagram"] = "1"
                upgrade_canvasitem(item, "1.0.0")
        parsed_data = {
            "1": element(id="1", type="Diagram"),
            **{p.id: p for p in parsed_items},
        }
        load_elements(parsed_data, element_factory, modeling_language)
        return list(element_factory.lselect()[0].get_all_items())

    return _loader


def test_upgrade_metaclass_item_to_class_item(loader):
    item = loader(element(id="2", type="MetaclassItem"))[0]

    assert type(item) is diagramitems.ClassItem


def test_upgrade_subsystem_item_to_class_item(loader):
    item = loader(element(id="2", type="SubsystemItem"))[0]

    assert type(item) is diagramitems.ComponentItem


def test_rename_stereotype_attrs_field(loader):
    parsed_item = element(id="2", type="ClassItem")
    parsed_item.values["show_stereotypes_attrs"] = "1"
    item = loader(parsed_item)[0]

    assert not hasattr(item, "show_stereotypes_attrs")
    assert item.show_stereotypes


def test_rename_show_attributes_and_operations_field(loader):
    parsed_item = element(id="2", type="ClassItem")
    parsed_item.values["show-attributes"] = "0"
    parsed_item.values["show-operations"] = "0"
    item = loader(parsed_item)[0]

    assert not item.show_attributes
    assert not item.show_operations


def test_interface_drawing_style_normal(loader):
    parsed_item = element(id="2", type="InterfaceItem")
    parsed_item.values["drawing-style"] = "0"  # DRAW_NONE
    item = loader(parsed_item)[0]

    assert item.folded.name == "NONE"


def test_interface_drawing_style_folded(loader):
    parsed_item = element(id="2", type="InterfaceItem")
    parsed_item.values["drawing-style"] = "3"  # DRAW_ICON
    item = loader(parsed_item)[0]

    assert item.folded.name == "PROVIDED"


def test_upgrade_generalization_arrow_direction(loader):
    cls1 = element(id="2", type="ClassItem")
    cls2 = element(id="3", type="ClassItem")
    gen_item = element(id="4", type="GeneralizationItem")
    gen_item.references["head-connection"] = ["2"]
    gen_item.references["tail-connection"] = ["3"]

    cls1, cls2, gen_item = loader(cls1, cls2, gen_item)

    assert gen_item.diagram.connections.get_connection(gen_item.head).connected is cls2
    assert gen_item.diagram.connections.get_connection(gen_item.tail).connected is cls1


def test_upgrade_flow_item_to_control_flow_item(element_factory, modeling_language):
    diagram = element(id="1", type="Diagram")
    objnode = element(id="2", type="ControlFlow")
    item = element(id="3", type="FlowItem")
    item.references["diagram"] = diagram.id
    item.references["subject"] = objnode.id

    load_elements(
        {p.id: p for p in (diagram, objnode, item)}, element_factory, modeling_language
    )

    assert element_factory.lselect(diagramitems.ControlFlowItem)


def test_upgrade_flow_item_to_object_flow_item(element_factory, modeling_language):
    diagram = element(id="1", type="Diagram")
    objnode = element(id="2", type="ObjectFlow")
    item = element(id="3", type="FlowItem")
    item.references["diagram"] = diagram.id
    item.references["subject"] = objnode.id

    load_elements(
        {p.id: p for p in (diagram, objnode, item)}, element_factory, modeling_language
    )

    assert element_factory.lselect(diagramitems.ObjectFlowItem)


def test_upgrade_decision_node_item_show_type(loader):
    parsed_item = element(id="2", type="DecisionNodeItem")
    parsed_item.values["show_type"] = "1"
    item = loader(parsed_item)[0]

    assert item.show_underlying_type == 1


@pytest.mark.parametrize("type", ["Property", "Port", "ProxyPort"])
def test_upgrade_delete_property_information_flow(
    element_factory, modeling_language, type
):
    prop = element(id="1", type=type)
    iflow = element(id="2", type="InformationFlow")
    prop.references["informationFlow"] = ["1"]

    load_elements({e.id: e for e in (prop, iflow)}, element_factory, modeling_language)

    assert element_factory.lselect(modeling_language.lookup_element(type))
    assert element_factory.lselect(modeling_language.lookup_element("InformationFlow"))


def test_upgrade_note_on_model_element(loader, element_factory):
    cls_item = element(id="2", type="ClassItem")
    cls = element(id="3", type="Class")
    cls_item.values["note"] = "my note"
    cls_item.references["subject"] = cls.id

    loader(cls_item, cls)
    _, cls_item, cls, *_ = element_factory.lselect()

    assert not cls_item.note
    assert cls.note == "my note"


def test_upgrade_append_notes_on_model_element(loader, element_factory):
    cls_item1 = element(id="2", type="ClassItem")
    cls_item2 = element(id="3", type="ClassItem")
    cls = element(id="44", type="Class")
    cls_item1.values["note"] = "my note"
    cls_item1.references["subject"] = cls.id
    cls_item2.values["note"] = "another note"
    cls_item2.references["subject"] = cls.id

    loader(cls_item1, cls_item2, cls)
    _, cls_item1, cls_item2, cls, *_ = element_factory.lselect()

    assert not cls_item1.note
    assert not cls_item2.note
    assert cls.note == "my note\n\nanother note"
