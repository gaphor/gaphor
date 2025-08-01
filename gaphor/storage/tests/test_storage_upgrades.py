import itertools

import pytest

from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.load import (
    load_elements,
    sysml_diagram_type_to_class,
    uml_diagram_type_to_class,
)
from gaphor.storage.parser import element
from gaphor.storage.upgrade_canvasitem import upgrade_canvasitem
from gaphor.UML import Dependency, Diagram, Image, Package, diagramitems


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

    assert cls.note == "my note\n\nanother note"


def test_upgrade_picture_to_image(loader, element_factory):
    picture = element(id="2", type="Picture")
    picture_item = element(id="3", type="PictureItem")

    loader(picture, picture_item)
    _, image, image_item, *_ = element_factory.lselect()

    assert isinstance(image, Image)
    assert isinstance(image_item, diagramitems.ImageItem)


def test_upgrade_diagram_to_uml_diagram(loader, element_factory):
    diagram = element(id="2", type="Diagram")
    core_diagram = element(id="3", type="Diagram", ns="Core")

    loader(diagram, core_diagram)
    _, new_diagram, new_core_diagram, *_ = element_factory.lselect()

    assert isinstance(new_diagram, Diagram)
    assert isinstance(new_core_diagram, Diagram)


def test_upgrade_dependency_owning_package(loader, element_factory):
    pkg = element(id="2", type="Package")
    pkg.references["ownedDiagram"] = ["1"]
    cls_item1 = element(id="3", type="ClassItem")
    cls1 = element(id="30", type="Class")
    cls_item1.references["subject"] = cls1.id
    cls_item2 = element(id="4", type="ClassItem")
    cls2 = element(id="40", type="Class")
    cls_item2.references["subject"] = cls2.id
    dep_item = element(id="5", type="DependencyItem", ns="UML")
    dep = element(id="50", type="Dependency", ns="UML")
    dep_item.references["subject"] = dep.id
    dep.references["supplier"] = [cls1.id]
    dep.references["client"] = [cls2.id]

    loader(cls_item1, cls_item2, dep_item, pkg, dep, cls1, cls2)
    new_pkg = next(element_factory.select(Package))
    new_dep = next(element_factory.select(Dependency))

    assert new_dep.owner is new_pkg


@pytest.mark.parametrize(
    "orig_type,kind,ns,new_type",
    [
        ["Diagram", "", "UML", "Diagram"],
        ["Diagram", "cls", "UML", "ClassDiagram"],
        ["Diagram", "pkg", "UML", "PackageDiagram"],
        ["Diagram", "cmp", "UML", "ComponentDiagram"],
        ["Diagram", "dep", "UML", "DeploymentDiagram"],
        ["Diagram", "prf", "UML", "ProfileDiagram"],
        ["Diagram", "act", "UML", "ActivityDiagram"],
        ["Diagram", "sd", "UML", "SequenceDiagram"],
        ["Diagram", "com", "UML", "CommunicationDiagram"],
        ["Diagram", "stm", "UML", "StateMachineDiagram"],
        ["Diagram", "uc", "UML", "UseCaseDiagram"],
        ["Diagram", "bdd", "SysML", "BlockDefinitionDiagram"],
        ["Diagram", "bdd", "SysML", "BlockDefinitionDiagram"],
        ["Diagram", "ibd", "SysML", "InternalBlockDiagram"],
        ["Diagram", "req", "SysML", "RequirementDiagram"],
        ["SysMLDiagram", "bdd", "SysML", "BlockDefinitionDiagram"],
        ["SysMLDiagram", "ibd", "SysML", "InternalBlockDiagram"],
        ["SysMLDiagram", "par", "SysML", "ParametricDiagram"],
        ["SysMLDiagram", "pkg", "SysML", "PackageDiagram"],
        ["SysMLDiagram", "req", "SysML", "RequirementDiagram"],
        ["SysMLDiagram", "act", "SysML", "ActivityDiagram"],
        ["SysMLDiagram", "sd", "SysML", "SequenceDiagram"],
        ["SysMLDiagram", "stm", "SysML", "StateMachineDiagram"],
        ["SysMLDiagram", "uc", "SysML", "UseCaseDiagram"],
    ],
)
def test_diagram_type_to_class(
    orig_type, kind, ns, new_type, element_factory, modeling_language
):
    e = element(id="1", type=orig_type)
    e.values["diagramType"] = kind

    load_elements({"1": e}, element_factory, modeling_language)
    diagram = next(element_factory.select())
    expected_type = modeling_language.lookup_element(new_type, ns)

    assert type(diagram) is expected_type


@pytest.mark.parametrize(
    "kind,ns,name",
    (
        [(k, n, m) for k, (n, m) in uml_diagram_type_to_class.items()]
        + [(k, n, m) for k, (n, m) in sysml_diagram_type_to_class.items()]
    ),
)
def test_diagram_type_to_class_mapping(kind, ns, name):
    modeling_language = ModelingLanguageService()
    diagram_class = modeling_language.lookup_element(name, ns)

    assert diagram_class.diagramType.default == kind


@pytest.mark.parametrize(
    "element_type,property_name,value,literal_type,expected_value",
    [
        ["MultiplicityElement", "lowerValue", "1", "LiteralInteger", 1],
        ["MultiplicityElement", "lowerValue", "", "NoneType", None],
        ["MultiplicityElement", "lowerValue", None, "NoneType", None],
        ["MultiplicityElement", "upperValue", "1", "LiteralUnlimitedNatural", 1],
        ["MultiplicityElement", "upperValue", "*", "LiteralUnlimitedNatural", "*"],
        ["MultiplicityElement", "upperValue", "", "LiteralUnlimitedNatural", "*"],
        ["MultiplicityElement", "upperValue", None, "NoneType", None],
        *(
            a[0] + a[1]
            for a in itertools.product(
                [
                    ["Parameter", "defaultValue"],
                    ["Slot", "value"],
                    ["ValueSpecificationAction", "value"],
                    ["InstanceSpecification", "specification"],
                    ["Constraint", "specification"],
                    ["ActivityEdge", "guard"],
                    ["ControlFlow", "guard"],
                    ["ObjectFlow", "guard"],
                    ["JoinNode", "joinSpec"],
                ],
                [
                    ["value", "LiteralString", "value"],
                    ['"value"', "LiteralString", "value"],
                    ["1", "LiteralInteger", 1],
                    ["*", "LiteralUnlimitedNatural", "*"],
                    ["true", "LiteralBoolean", True],
                    ["True", "LiteralBoolean", True],
                    ["false", "LiteralBoolean", False],
                    ["False", "LiteralBoolean", False],
                    ["", "LiteralString", ""],
                    [None, "LiteralString", None],
                    ['"', "LiteralString", ""],
                    ["-1", "LiteralString", "-1"],
                    ["1a", "LiteralString", "1a"],
                ],
            )
        ),
    ],
)
def test_update_value_to_value_specification(
    element_type,
    property_name,
    value,
    literal_type,
    expected_value,
    element_factory,
    modeling_language,
):
    e = element(id="1", type=element_type)
    e.values[property_name] = value

    load_elements({"1": e}, element_factory, modeling_language)

    p = element_factory.lookup("1")
    value_spec = getattr(p, property_name)

    assert type(p).__name__ == element_type
    assert type(value_spec).__name__ == literal_type

    if value_spec is not None:
        assert value_spec.value == expected_value
        assert value_spec in element_factory


@pytest.mark.parametrize(
    "element_type",
    [
        "LiteralString",
        "LiteralInteger",
        "LiteralBoolean",
        "LiteralUnlimitedNatural",
        "LiteralSpecification",
    ],
)
def test_do_not_update_value_for_literal_specification(
    element_type, element_factory, modeling_language
):
    e = element(id="1", type=element_type)
    e.values["value"] = "1"

    load_elements({"1": e}, element_factory, modeling_language)

    p = element_factory.lookup("1")

    assert type(p).__name__ == element_type
    assert str(p.value) == "1"


def test_update_parameter_default_direction(element_factory, modeling_language):
    e = element(id="2", type="Parameter")
    e.values["direction"] = "out"

    load_elements(
        {"1": element(id="1", type="Parameter"), "2": e},
        element_factory,
        modeling_language,
    )

    p1 = element_factory.lookup("1")
    p2 = element_factory.lookup("2")

    assert p1.direction == "inout"
    assert p2.direction == "out"


@pytest.mark.parametrize(
    "element_type",
    [
        "ObjectNode",
        "ActivityParameterNode",
        "Pin",
        "InputPin",
        "OutputPin",
    ],
)
def test_update_object_node_default_ordering(
    element_type, element_factory, modeling_language
):
    load_elements(
        {"1": element(id="1", type=element_type)}, element_factory, modeling_language
    )

    p = element_factory.lookup("1")

    assert p.ordering == "unordered"
