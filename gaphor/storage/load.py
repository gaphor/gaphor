"""Load Gaphor models to Gaphors own XML format.

One function is exported: `load(file_obj)` loads a model from a
file.
"""

__all__ = ["load"]

import io
import logging
from collections.abc import Callable, Iterable

from gaphor.core.modeling import Base, Diagram, ElementFactory, Id, Presentation
from gaphor.core.modeling.modelinglanguage import ModelingLanguage
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.storage.parser import GaphorLoader, element, parse_generator

log = logging.getLogger(__name__)


def load_elements(
    elements: dict[Id, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    gaphor_version="1.0.0",
) -> None:
    for _ in load_elements_generator(
        elements, element_factory, modeling_language, gaphor_version
    ):
        pass


def load_elements_generator(
    elements: dict[Id, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    gaphor_version: str,
) -> Iterable[float]:
    """Load a file and create a model if possible.

    Exceptions: IOError, ValueError.
    """

    def maybe_upgrade(upgrade_func, *args) -> None:
        if version_lower_than(gaphor_version, upgrade_func.__since__):
            upgrade_func(*args)

    log.debug(f"Loading {len(elements)} elements")

    # The elements are iterated three times:
    size = len(elements) * 3
    progress = 0

    def update_status_queue() -> Iterable[float]:
        nonlocal progress, size
        progress += 1
        if progress % 30 == 0:
            yield (progress * 100) / size

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    yield from _load_elements_and_canvasitems(
        elements,
        element_factory,
        modeling_language,
        maybe_upgrade,
        update_status_queue,
    )
    maybe_upgrade(upgrade_package_package_to_nesting_package, elements)
    maybe_upgrade(upgrade_parameter_owned_node_to_activity_parameter_node, elements)
    maybe_upgrade(upgrade_enumeration_default_values, elements)

    yield from _load_attributes_and_references(
        elements, element_factory, update_status_queue
    )

    upgrade_ensure_style_sheet_is_present(element_factory)
    maybe_upgrade(upgrade_dependency_owning_package, element_factory, modeling_language)

    for _id, elem in list(elements.items()):
        yield from update_status_queue()
        assert elem.element
        elem.element.postload()

    for diagram in element_factory.select(Diagram):
        diagram.update()


def _load_elements_and_canvasitems(  # type: ignore[explicit-any]
    elements: dict[Id, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    maybe_upgrade: Callable[..., None],
    update_status_queue: Callable[[], Iterable[float]],
) -> Iterable[float]:
    def create_element(elem):
        if elem.element:
            return

        maybe_upgrade(upgrade_element_owned_comment_to_comment, elem)
        maybe_upgrade(upgrade_package_owned_classifier_to_owned_type, elem)
        maybe_upgrade(upgrade_implementation_to_interface_realization, elem)
        maybe_upgrade(upgrade_feature_parameters_to_owned_parameter, elem)
        maybe_upgrade(upgrade_parameter_owner_formal_param, elem)
        maybe_upgrade(upgrade_diagram_element, elem)
        maybe_upgrade(upgrade_generalization_arrow_direction, elem)
        maybe_upgrade(upgrade_flow_item_to_control_flow_item, elem, elements)
        maybe_upgrade(upgrade_delete_property_information_flow, elem)
        maybe_upgrade(upgrade_decision_node_item_show_type, elem)
        maybe_upgrade(upgrade_note_on_model_element_only, elem, elements)
        maybe_upgrade(upgrade_modeling_language, elem)
        maybe_upgrade(upgrade_diagram_type_to_class, elem)
        maybe_upgrade(
            upgrade_simple_properties_to_value_specifications,
            elem,
            element_factory,
            modeling_language,
        )

        if not (cls := modeling_language.lookup_element(elem.type, elem.ns)):
            raise UnknownModelElementError(
                f"Type {elem.ns}:{elem.type} cannot be loaded: no such element"
            )

        if issubclass(cls, Presentation):
            if "diagram" not in elem.references:
                log.warning(
                    "Removing element %s of type %s without diagram", elem.id, cls
                )
                assert all(elem.id not in e.references for e in elements.values())
                del elements[elem.id]
                return

            diagram_id = elem.references["diagram"]
            diagram_elem = elements[diagram_id]
            create_element(diagram_elem)
            assert isinstance(diagram_elem.element, Diagram)
            elem.element = element_factory.create_as(cls, elem.id, diagram_elem.element)
        else:
            elem.element = element_factory.create_as(cls, elem.id)

    for _id, elem in list(elements.items()):
        yield from update_status_queue()
        create_element(elem)


def _load_attributes_and_references(
    elements: dict[Id, element],
    element_factory: ElementFactory,
    update_status_queue: Callable[[], Iterable[float]],
) -> Iterable[float]:
    for _id, elem in list(elements.items()):
        yield from update_status_queue()
        # Ensure that all elements have their element instance ready...
        assert elem.element

        # load attributes and references:
        for name, value in list(elem.values.items()):
            try:
                elem.element.load(name, value)
            except AttributeError:
                log.exception(f"Invalid attribute name {elem.type}.{name}")

        ref: element | None
        for name, refids in list(elem.references.items()):
            if isinstance(refids, list):
                for refid in refids:
                    try:
                        ref = elements[refid]
                    except KeyError:
                        log.exception(
                            f"Invalid ID for reference ({refid}) for element {elem.type}.{name}"
                        )
                    else:
                        assert ref.element
                        elem.element.load(name, ref.element)
            else:
                if ref := elements.get(refids):
                    assert ref.element
                    elem.element.load(name, ref.element)
                elif ref_elem := element_factory.lookup(refids):
                    # Element may have been created by an updater
                    elem.element.load(name, ref_elem)
                else:
                    log.exception(f"Invalid ID for reference ({refids})")


def load(
    file_obj: io.TextIOBase,
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    status_queue: Callable[[int], None] | None = None,
) -> None:
    """Load a file and create a model if possible.

    Optionally, a status queue function can be given, to which the
    progress is written (as status_queue(progress)).
    """
    for status in load_generator(file_obj, element_factory, modeling_language):
        if status_queue:
            status_queue(status)


def load_generator(
    file_obj: io.TextIOBase,
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
) -> Iterable[int]:
    """Load a file and create a model if possible.

    This function is a generator. It will yield values from 0 to 100 (%)
    to indicate its progression.
    """
    assert isinstance(file_obj, io.TextIOBase)

    # Use the incremental parser and yield the percentage of the file.
    loader = GaphorLoader()
    for percentage in parse_generator(file_obj, loader):
        if percentage:
            yield percentage / 2
        else:
            yield percentage

    elements = loader.elements
    gaphor_version = loader.gaphor_version

    if version_lower_than(gaphor_version, (0, 17, 0)):
        raise ValueError(
            f"Gaphor model version should be at least 0.17.0 (found {gaphor_version})"
        )

    log.info(f"Read {len(elements)} elements from file")

    element_factory.flush()
    with element_factory.block_events():
        for percentage in load_elements_generator(
            elements, element_factory, modeling_language, gaphor_version
        ):
            if percentage:
                yield int(percentage / 2 + 50)
            else:
                yield int(percentage)

    yield 100


def version_lower_than(gaphor_version: str, version: tuple[int, ...]) -> bool:
    """Only major and minor versions are checked.

    >>> version_lower_than("0.3.0", (0, 15, 0))
    True
    """
    parts = gaphor_version.split(".")

    return tuple(map(int, parts[:2])) < version[:2]


class UnknownModelElementError(Exception):
    pass


def since(major, minor, patch=0):
    def _since(func):
        func.__since__ = (major, minor, patch)
        return func

    return _since


@since(2, 1, 0)
def upgrade_element_owned_comment_to_comment(elem: element):
    for name, refids in dict(elem.references).items():
        if name == "ownedComment":
            elem.references["comment"] = refids
            del elem.references["ownedComment"]
            break


@since(2, 2, 0)
def upgrade_ensure_style_sheet_is_present(factory: ElementFactory) -> None:
    style_sheet = next(factory.select(StyleSheet), None)
    if not style_sheet:
        factory.create(StyleSheet)


@since(2, 3, 0)
def upgrade_package_owned_classifier_to_owned_type(elem: element) -> None:
    for name, refids in dict(elem.references).items():
        if name == "ownedClassifier":
            elem.references["ownedType"] = refids
            del elem.references["ownedClassifier"]
            break


@since(2, 3, 0)
def upgrade_implementation_to_interface_realization(elem: element) -> None:
    if elem.type == "Implementation":
        elem.type = "InterfaceRealization"


@since(2, 3, 0)
def upgrade_feature_parameters_to_owned_parameter(elem: element) -> None:
    formal_params: list[Id] = []
    return_results: list[Id] = []
    for name, refids in dict(elem.references).items():
        if name == "formalParameter":
            formal_params = refids  # type: ignore[assignment]
            del elem.references["formalParameter"]
        elif name == "returnResult":
            return_results = refids  # type: ignore[assignment]
            del elem.references["returnResult"]
    elem.references["ownedParameter"] = formal_params + return_results


@since(2, 3, 0)
def upgrade_parameter_owner_formal_param(elem: element) -> None:
    for name, refids in dict(elem.references).items():
        if name == "ownerReturnParam":
            elem.references["ownerFormalParam"] = refids
            del elem.references["ownerReturnParam"]
            break


@since(2, 5, 0)
def upgrade_diagram_element(elem: element) -> None:
    if elem.type == "Diagram":
        for name, refids in dict(elem.references).items():
            if name == "package":
                elem.references["element"] = refids
                del elem.references["package"]
                break


@since(2, 6, 0)
def upgrade_generalization_arrow_direction(elem: element) -> None:
    if elem.type == "GeneralizationItem":
        head_id: str | None = None
        tail_id: str | None = None
        for name, refids in dict(elem.references).items():
            if name == "head-connection":
                head_id = refids  # type: ignore[assignment]
            elif name == "tail-connection":
                tail_id = refids  # type: ignore[assignment]
        if head_id and tail_id:
            elem.references["head-connection"], elem.references["tail-connection"] = (
                tail_id,
                head_id,
            )


@since(2, 9, 0)
def upgrade_flow_item_to_control_flow_item(
    elem: element, elements: dict[Id, element]
) -> None:
    if elem.type == "FlowItem":
        if subject_id := elem.references.get("subject"):
            subject_type = elements[subject_id].type  # type: ignore[index]
        else:
            subject_type = "ControlFlow"

        elem.type = f"{subject_type}Item"


@since(2, 19, 0)
def upgrade_decision_node_item_show_type(elem: element) -> None:
    if elem.type == "DecisionNodeItem":
        if "show_type" in elem.values:
            elem.values["show_underlying_type"] = elem.values["show_type"]
            del elem.values["show_type"]


@since(2, 19, 0)
def upgrade_delete_property_information_flow(elem: element) -> None:
    if (
        elem.type in ("Property", "Port", "ProxyPort")
        and "informationFlow" in elem.references
    ):
        del elem.references["informationFlow"]


@since(2, 20, 0)
def upgrade_note_on_model_element_only(
    elem: element, elements: dict[Id, element]
) -> None:
    if elem.type.endswith("Item") and "note" in elem.values:
        if subject := elements.get(elem.references.get("subject", None)):  # type: ignore[arg-type]
            if (
                subject.values.get("note")
                and isinstance(subject.values["note"], str)
                and isinstance(elem.values["note"], str)
            ):
                subject.values["note"] = (
                    str(subject.values["note"]) + "\n\n" + str(elem.values["note"])
                )
            else:
                subject.values["note"] = elem.values["note"]
            del elem.values["note"]


@since(2, 28, 0)
def upgrade_modeling_language(elem: element) -> None:
    if elem.type == "Diagram" and elem.ns in (None, "", "Core"):
        elem.ns = "UML"
    elif elem.ns:
        pass
    elif elem.type == "Dependency":
        elem.ns = "UML"
    elif elem.type in ("C4Person", "C4Container", "C4Database", "C4Dependency"):
        elem.type = elem.type[2:]
        elem.ns = "C4Model"
    elif elem.type == "Picture":
        elem.ns = "UML"
        elem.type = "Image"
    elif elem.type == "PictureItem":
        elem.ns = "UML"
        elem.type = "ImageItem"


@since(2, 28, 0)
def upgrade_dependency_owning_package(
    element_factory: ElementFactory, modeling_language
):
    Dependency = modeling_language.lookup_element("Dependency", ns="UML")
    Package = modeling_language.lookup_element("Package", ns="UML")
    for dep in element_factory.select(Dependency):
        if not dep.presentation:
            continue

        maybe_pkg = dep.presentation[0].diagram
        while maybe_pkg:
            if isinstance(maybe_pkg, Package):
                dep.owningPackage = maybe_pkg
                break
            maybe_pkg = maybe_pkg.owner


@since(2, 28, 0)
def upgrade_diagram_type_to_class(elem: element) -> None:
    if elem.type == "Diagram":
        if diagram_type := elem.values.get("diagramType"):
            assert isinstance(diagram_type, str)
            elem.ns, elem.type = uml_diagram_type_to_class[diagram_type]
    elif elem.type == "SysMLDiagram":
        if diagram_type := elem.values.get("diagramType"):
            assert isinstance(diagram_type, str)
            elem.ns, elem.type = sysml_diagram_type_to_class[diagram_type]


uml_diagram_type_to_class = {
    "cls": ("UML", "ClassDiagram"),
    "pkg": ("UML", "PackageDiagram"),
    "cmp": ("UML", "ComponentDiagram"),
    "dep": ("UML", "DeploymentDiagram"),
    "act": ("UML", "ActivityDiagram"),
    "sd": ("UML", "SequenceDiagram"),
    "com": ("UML", "CommunicationDiagram"),
    "stm": ("UML", "StateMachineDiagram"),
    "uc": ("UML", "UseCaseDiagram"),
    "prf": ("UML", "ProfileDiagram"),
    "fta": ("RAAML", "FTADiagram"),
    "stpa": ("RAAML", "STPADiagram"),
    "c4": ("C4Model", "C4Diagram"),
    "bdd": ("SysML", "BlockDefinitionDiagram"),
    "ibd": ("SysML", "InternalBlockDiagram"),
    "req": ("SysML", "RequirementDiagram"),
}

sysml_diagram_type_to_class = {
    "act": ("SysML", "ActivityDiagram"),
    "bdd": ("SysML", "BlockDefinitionDiagram"),
    "ibd": ("SysML", "InternalBlockDiagram"),
    "pkg": ("SysML", "PackageDiagram"),
    "req": ("SysML", "RequirementDiagram"),
    "sd": ("SysML", "SequenceDiagram"),
    "stm": ("SysML", "StateMachineDiagram"),
    "uc": ("SysML", "UseCaseDiagram"),
    "par": ("SysML", "ParametricDiagram"),
}


@since(3, 1, 0)
def upgrade_simple_properties_to_value_specifications(
    elem: element,
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
) -> None:
    valueSpecification = modeling_language.lookup_element("ValueSpecification", "UML")
    element_type = modeling_language.lookup_element(elem.type, elem.ns)
    for name, value in dict(elem.values).items():
        match name:
            case "upperValue":
                value_attr = getattr(element_type, "upperValue", None)
                if value_attr and value_attr.type == valueSpecification:
                    type = modeling_language.lookup_element(
                        "LiteralUnlimitedNatural", elem.ns
                    )
                    if type is not None and isinstance(value, str):
                        upper_value = element_factory.create(type)
                        try:
                            # Overwrite any string value that is not '*'
                            upper_value.value = int(value)
                        except ValueError:
                            upper_value.value = "*"
                        upper_value.name = value
                        del elem.values["upperValue"]
                        elem.references["upperValue"] = upper_value.id
            case "lowerValue":
                value_attr = getattr(element_type, "lowerValue", None)
                if value_attr and value_attr.type == valueSpecification:
                    type = modeling_language.lookup_element("LiteralInteger", elem.ns)
                    if type is not None and isinstance(value, str):
                        try:
                            int_value = int(value)
                        except ValueError:
                            pass
                        else:
                            lower_value = element_factory.create(type)
                            lower_value.value = int_value
                            lower_value.name = value
                            del elem.values["lowerValue"]
                            elem.references["lowerValue"] = lower_value.id
            case "defaultValue" | "joinSpec" | "specification" | "value":
                value_attr = getattr(element_type, name, None)
                if value_attr and value_attr.type == valueSpecification:
                    value_spec = _value_specification_from_value(
                        value, elem, element_factory, modeling_language
                    )
                    if value_spec is not None:
                        del elem.values[name]
                        elem.references[name] = value_spec.id
            case "guard" if elem.type in ("ActivityEdge", "ControlFlow", "ObjectFlow"):
                value_attr = getattr(element_type, name, None)
                if value_attr and value_attr.type == valueSpecification:
                    value_spec = _value_specification_from_value(
                        value, elem, element_factory, modeling_language
                    )
                    if value_spec is not None:
                        del elem.values["guard"]
                        elem.references["guard"] = value_spec.id


def _value_specification_from_value(
    value: str | None,
    elem: element,
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
) -> Base | None:
    value_spec: Base | None = None
    if value and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
        type = modeling_language.lookup_element("LiteralString", elem.ns)
        assert type
        value_spec = element_factory.create(type)
        value_spec.value = value
        value_spec.name = value
    elif value in ["true", "True", "false", "False"]:
        type = modeling_language.lookup_element("LiteralBoolean", elem.ns)
        assert type
        value_spec = element_factory.create(type)
        if value in ["true", "True"]:
            value_spec.value = True
        else:
            value_spec.value = False
        value_spec.name = value
    elif value == "*":
        type = modeling_language.lookup_element("LiteralUnlimitedNatural", elem.ns)
        assert type
        value_spec = element_factory.create(type)
        value_spec.value = value
        value_spec.name = value
    elif value and value.isdigit():
        type = modeling_language.lookup_element("LiteralInteger", elem.ns)
        assert type
        value_spec = element_factory.create(type)
        value_spec.value = int(value)
        value_spec.name = value
    else:
        # Anything else we assume as string.
        type = modeling_language.lookup_element("LiteralString", elem.ns)
        assert type
        value_spec = element_factory.create(type)
        value_spec.value = value
        value_spec.name = value

    return value_spec


@since(3, 1, 0)
def upgrade_package_package_to_nesting_package(elements: dict[Id, element]) -> None:
    for _id, elem in list(elements.items()):
        if elem.type in ["Package", "Profile"]:
            if "package" in elem.references:
                elem.references["nestingPackage"] = elem.references["package"]
                del elem.references["package"]


@since(3, 1, 0)
def upgrade_parameter_owned_node_to_activity_parameter_node(
    elements: dict[Id, element],
) -> None:
    for _id, elem in list(elements.items()):
        if elem.type == "Parameter":
            if "owningNode" in elem.references:
                elem.references["activityParameterNode"] = elem.references["owningNode"]
                del elem.references["owningNode"]


@since(3, 2, 0)
def upgrade_enumeration_default_values(
    elements: dict[Id, element],
) -> None:
    for _id, elem in list(elements.items()):
        if elem.type == "Parameter" and "direction" not in elem.values:
            elem.values["direction"] = "inout"
        if (
            elem.type
            in ("ObjectNode", "ActivityParameterNode", "Pin", "InputPin", "OutputPin")
            and "ordering" not in elem.values
        ):
            elem.values["ordering"] = "unordered"
