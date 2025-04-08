"""Load and save Gaphor models to Gaphors own XML format.

Three functions are exported: `load(file_obj)`loads a model from a
file. `save(file_obj)` stores the current model in a file.
"""

__all__ = ["load", "save"]

import io
import logging
from collections.abc import Callable, Iterable
from functools import partial

from gaphor import application
from gaphor.core.modeling import Base, Diagram, ElementFactory, Presentation
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.modelinglanguage import ModelingLanguage
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.storage.parser import GaphorLoader, element, parse_generator
from gaphor.storage.xmlwriter import XMLWriter

FILE_FORMAT_VERSION = "4"
MODEL_NS = "https://gaphor.org/model"
MODELING_LANGUAGE_NS = "https://gaphor.org/modelinglanguage"

log = logging.getLogger(__name__)


def save(out=None, element_factory=None, status_queue=None):
    for status in save_generator(out, element_factory):
        if status_queue:
            status_queue(status)


def save_generator(out, element_factory: ElementFactory):
    """Save the current model using @writer, which is a
    gaphor.storage.xmlwriter.XMLWriter instance."""

    with XMLWriter(out).document() as writer:
        writer.prefix_mapping("", MODEL_NS)
        for ml in sorted({e.__modeling_language__ for e in element_factory}):
            writer.prefix_mapping(ml, f"{MODELING_LANGUAGE_NS}/{ml}")

        with writer.element_ns(
            (MODEL_NS, "gaphor"),
            {
                (MODEL_NS, "version"): FILE_FORMAT_VERSION,
                (MODEL_NS, "gaphor-version"): application.distribution().version,
            },
        ):
            with writer.element_ns((MODEL_NS, "model"), {}):
                size = element_factory.size()
                save_func = partial(
                    save_element, element_factory=element_factory, writer=writer
                )
                for n, e in enumerate(element_factory, start=1):
                    clazz = e.__class__.__name__
                    assert e.id
                    ns = f"{MODELING_LANGUAGE_NS}/{e.__modeling_language__}"
                    with writer.element_ns((ns, clazz), {(MODEL_NS, "id"): str(e.id)}):
                        e.save(save_func)

                    if n % 25 == 0:
                        yield (n * 100) / size


def save_element(name, value, element_factory, writer):
    """Save attributes and references from items in the gaphor.UML module.

    A value may be a primitive (string, int), a
    gaphor.core.modeling.collection (which contains a list of references
    to other UML elements) or a Diagram (which contains diagram items).
    """

    def resolvable(value):
        if value.id and value in element_factory:
            return True
        log.warning(
            f"Model has unknown reference {value.id}. Reference will be skipped."
        )
        return False

    def save_reference(name, value):
        """Save a value as a reference to another element in the model.

        This applies to both UML and canvas items.
        """
        if resolvable(value):
            with writer.element(name, {}):
                with writer.element("ref", {"refid": value.id}):
                    pass

    def save_collection(name, value):
        """Save a list of references."""
        if value:
            with writer.element(name, {}):
                with writer.element("reflist", {}):
                    for v in value:
                        if resolvable(v):
                            with writer.element("ref", {"refid": v.id}):
                                pass

    def save_value(name, value):
        """Save a value (attribute)."""
        if value is not None:
            with writer.element(name, {}):
                with writer.element("val", {}):
                    writer.characters(str(value))

    if isinstance(value, Base):
        save_reference(name, value)
    elif isinstance(value, collection):
        save_collection(name, value)
    else:
        save_value(name, value)


def load_elements(elements, element_factory, modeling_language, gaphor_version="1.0.0"):
    for _ in load_elements_generator(
        elements, element_factory, modeling_language, gaphor_version
    ):
        pass


def load_elements_generator(
    elements: dict[str, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    gaphor_version: str,
) -> Iterable[float]:
    """Load a file and create a model if possible.

    Exceptions: IOError, ValueError.
    """
    log.debug(f"Loading {len(elements)} elements")

    # The elements are iterated three times:
    size = len(elements) * 3
    progress = 0

    def update_status_queue() -> Iterable[float]:
        nonlocal progress, size
        progress += 1
        if progress % 30 == 0:
            yield (progress * 100) / size

    homeless_literals: dict[str, element] = {}

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    yield from _load_elements_and_canvasitems(
        elements,
        element_factory,
        modeling_language,
        gaphor_version,
        update_status_queue,
        homeless_literals,
    )
    if version_lower_than(gaphor_version, (3, 1, 0)):
        upgrade_package_package_to_nesting_package(elements)
        upgrade_parameter_owned_node_to_activity_parameter_node(elements)

    yield from _load_attributes_and_references(elements, update_status_queue)

    upgrade_ensure_style_sheet_is_present(element_factory)
    if version_lower_than(gaphor_version, (2, 28, 0)):
        upgrade_dependency_owning_package(element_factory, modeling_language)

    for _id, elem in list(elements.items()):
        yield from update_status_queue()
        assert elem.element
        elem.element.postload()

    for diagram in element_factory.select(Diagram):
        diagram.update()

    house_homeless_literals(
        element_factory, homeless_literals, elements, modeling_language
    )


def _load_elements_and_canvasitems(
    elements: dict[str, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    gaphor_version: str,
    update_status_queue: Callable[[], Iterable[float]],
    homeless_literals: dict[str, element],
):
    def create_element(elem):
        if elem.element:
            return
        if version_lower_than(gaphor_version, (2, 1, 0)):
            elem = upgrade_element_owned_comment_to_comment(elem)
        if version_lower_than(gaphor_version, (2, 3, 0)):
            elem = upgrade_package_owned_classifier_to_owned_type(elem)
            elem = upgrade_implementation_to_interface_realization(elem)
            elem = upgrade_feature_parameters_to_owned_parameter(elem)
            elem = upgrade_parameter_owner_formal_param(elem)
        if version_lower_than(gaphor_version, (2, 5, 0)):
            elem = upgrade_diagram_element(elem)
        if version_lower_than(gaphor_version, (2, 6, 0)):
            elem = upgrade_generalization_arrow_direction(elem)
        if version_lower_than(gaphor_version, (2, 9, 0)):
            elem = upgrade_flow_item_to_control_flow_item(elem, elements)
        if version_lower_than(gaphor_version, (2, 19, 0)):
            elem = upgrade_delete_property_information_flow(elem)
            elem = upgrade_decision_node_item_show_type(elem)
        if version_lower_than(gaphor_version, (2, 20, 0)):
            elem = upgrade_note_on_model_element_only(elem, elements)
        if version_lower_than(gaphor_version, (2, 28, 0)):
            elem = upgrade_modeling_language(elem)
            elem = upgrade_diagram_type_to_class(elem)
        if version_lower_than(gaphor_version, (3, 1, 0)):
            elem = upgrade_simple_properties_to_value_specifications(
                elem, element_factory, modeling_language, homeless_literals
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


def _load_attributes_and_references(elements, update_status_queue):
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
                        elem.element.load(name, ref.element)
            else:
                try:
                    ref = elements[refids]
                except KeyError:
                    log.exception(f"Invalid ID for reference ({refids})")
                else:
                    elem.element.load(name, ref.element)


def load(
    file_obj: io.TextIOBase, element_factory, modeling_language, status_queue=None
):
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
                yield percentage / 2 + 50
            else:
                yield percentage

    yield 100


def version_lower_than(gaphor_version, version):
    """Only major and minor versions are checked.

    >>> version_lower_than("0.3.0", (0, 15, 0))
    True
    """
    parts = gaphor_version.split(".")

    return tuple(map(int, parts[:2])) < version[:2]


class UnknownModelElementError(Exception):
    pass


# since 2.1.0
def upgrade_element_owned_comment_to_comment(elem):
    for name, refids in dict(elem.references).items():
        if name == "ownedComment":
            elem.references["comment"] = refids
            del elem.references["ownedComment"]
            break
    return elem


# since 2.2.0
def upgrade_ensure_style_sheet_is_present(factory):
    style_sheet = next(factory.select(StyleSheet), None)
    if not style_sheet:
        factory.create(StyleSheet)


# since 2.3.0
def upgrade_package_owned_classifier_to_owned_type(elem):
    for name, refids in dict(elem.references).items():
        if name == "ownedClassifier":
            elem.references["ownedType"] = refids
            del elem.references["ownedClassifier"]
            break
    return elem


# since 2.3.0
def upgrade_implementation_to_interface_realization(elem):
    if elem.type == "Implementation":
        elem.type = "InterfaceRealization"
    return elem


# since 2.3.0
def upgrade_feature_parameters_to_owned_parameter(elem):
    formal_params = []
    return_results = []
    for name, refids in dict(elem.references).items():
        if name == "formalParameter":
            formal_params = refids
            del elem.references["formalParameter"]
        elif name == "returnResult":
            return_results = refids
            del elem.references["returnResult"]
    elem.references["ownedParameter"] = formal_params + return_results
    return elem


# since 2.3.0
def upgrade_parameter_owner_formal_param(elem):
    for name, refids in dict(elem.references).items():
        if name == "ownerReturnParam":
            elem.references["ownerFormalParam"] = refids
            del elem.references["ownerReturnParam"]
            break
    return elem


# since 2.5.0
def upgrade_diagram_element(elem):
    if elem.type == "Diagram":
        for name, refids in dict(elem.references).items():
            if name == "package":
                elem.references["element"] = refids
                del elem.references["package"]
                break
    return elem


# since 2.6.0
def upgrade_generalization_arrow_direction(elem):
    if elem.type == "GeneralizationItem":
        head_ids, tail_ids = 0, 0
        for name, refids in dict(elem.references).items():
            if name == "head-connection":
                head_ids = refids
            elif name == "tail-connection":
                tail_ids = refids
        if head_ids and tail_ids:
            elem.references["head-connection"], elem.references["tail-connection"] = (
                tail_ids,
                head_ids,
            )
    return elem


# since 2.9.0
def upgrade_flow_item_to_control_flow_item(elem, elements):
    if elem.type == "FlowItem":
        if subject_id := elem.references.get("subject"):
            subject_type = elements[subject_id].type
        else:
            subject_type = "ControlFlow"

        elem.type = f"{subject_type}Item"
    return elem


# since 2.19.0
def upgrade_decision_node_item_show_type(elem):
    if elem.type == "DecisionNodeItem":
        if "show_type" in elem.values:
            elem.values["show_underlying_type"] = elem.values["show_type"]
            del elem.values["show_type"]
    return elem


# since 2.19.0
def upgrade_delete_property_information_flow(elem):
    if (
        elem.type in ("Property", "Port", "ProxyPort")
        and "informationFlow" in elem.references
    ):
        del elem.references["informationFlow"]
    return elem


# since 2.20.0
def upgrade_note_on_model_element_only(
    elem: element, elements: dict[str, element]
) -> element:
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
    return elem


# since 2.28.0
def upgrade_modeling_language(elem: element) -> element:
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
    return elem


# since 2.28.0
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


# since 2.28.0
def upgrade_diagram_type_to_class(elem: element) -> element:
    if elem.type == "Diagram":
        if diagram_type := elem.values.get("diagramType"):
            assert isinstance(diagram_type, str)
            elem.ns, elem.type = uml_diagram_type_to_class[diagram_type]
    elif elem.type == "SysMLDiagram":
        if diagram_type := elem.values.get("diagramType"):
            assert isinstance(diagram_type, str)
            elem.ns, elem.type = sysml_diagram_type_to_class[diagram_type]
    return elem


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


# since 3.1.0
def upgrade_simple_properties_to_value_specifications(
    elem: element,
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    homeless_literals: dict,
) -> element:
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
                        upperValue = element_factory.create(type)
                        try:
                            # Overwrite any string value that is not '*'
                            upperValue.value = int(value)
                        except ValueError:
                            upperValue.value = "*"
                        upperValue.name = value
                        elem.values["upperValue"] = upperValue
                        homeless_literals[upperValue.id] = (elem.id, name)
            case "lowerValue":
                value_attr = getattr(element_type, "lowerValue", None)
                if value_attr and value_attr.type == valueSpecification:
                    type = modeling_language.lookup_element("LiteralInteger", elem.ns)
                    if type is not None and isinstance(value, str):
                        lowerValue = element_factory.create(type)
                        lowerValue.value = int(value)
                        lowerValue.name = value
                        elem.values["lowerValue"] = lowerValue
                        homeless_literals[lowerValue.id] = (elem.id, name)
            case "defaultValue" | "joinSpec" | "specification" | "value":
                value_attr = getattr(element_type, name, None)
                if value_attr and value_attr.type == valueSpecification:
                    defaultValue = get_value_specification_from_value(
                        value, elem, element_factory, modeling_language
                    )
                    if defaultValue is not None:
                        elem.values[name] = defaultValue
                        homeless_literals[defaultValue.id] = (elem.id, name)
            case "guard" if elem.type in ("ActivityEdge", "ControlFlow", "ObjectFlow"):
                value_attr = getattr(element_type, name, None)
                if value_attr and value_attr.type == valueSpecification:
                    defaultValue = get_value_specification_from_value(
                        value, elem, element_factory, modeling_language
                    )
                    if defaultValue is not None:
                        elem.values[name] = defaultValue
                        homeless_literals[defaultValue.id] = (elem.id, name)
    return elem


def get_value_specification_from_value(
    value, elem, element_factory, modeling_language
) -> Base | None:
    defaultValue = None
    if (len(value)!=0): 
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
            type = modeling_language.lookup_element("LiteralString", elem.ns)
            defaultValue = element_factory.create(type)
            defaultValue.value = value
            defaultValue.name = value
        elif value in ["true", "True", "false", "False"]:
            type = modeling_language.lookup_element("LiteralBoolean", elem.ns)
            defaultValue = element_factory.create(type)
            if value in ["true", "True"]:
                defaultValue.value = True
            else:
                defaultValue.value = False
            defaultValue.name = value
        elif value == "*":
            type = modeling_language.lookup_element("LiteralUnlimitedNatural", elem.ns)
            defaultValue = element_factory.create(type)
            defaultValue.value = value
            defaultValue.name = value
        elif value.isdigit():
            type = modeling_language.lookup_element("LiteralInteger", elem.ns)
            defaultValue = element_factory.create(type)
            defaultValue.value = int(value)
            defaultValue.name = value
        else:
            # Anything else we assume as string.
            type = modeling_language.lookup_element("LiteralString", elem.ns)
            defaultValue = element_factory.create(type)
            defaultValue.value = value
            defaultValue.name = value
    else:
        type = modeling_language.lookup_element("LiteralString", elem.ns)
        defaultValue = element_factory.create(type)
        defaultValue.value = value
        defaultValue.name = value


    if defaultValue and isinstance(defaultValue, Base):
        base_default_value: Base = defaultValue
        return base_default_value
    return None


def house_homeless_literals(
    element_factory: ElementFactory,
    homeless_literals: dict,
    elements: dict[str, element],
    modeling_language: ModelingLanguage,
):
    for literal_id, (elem_id, name) in homeless_literals.items():
        literal = element_factory.lookup(literal_id)
        elem = elements.get(elem_id)
        if elem is not None:
            element = elem.element
            setattr(element, name, literal)


# since 3.1.0
def upgrade_package_package_to_nesting_package(elements):
    for _id, elem in list(elements.items()):
        if elem.type in ["Package", "Profile"]:
            if "package" in elem.references:
                elem.references["nestingPackage"] = elem.references["package"]
                del elem.references["package"]


# since 3.1.0
def upgrade_parameter_owned_node_to_activity_parameter_node(elements):
    for _id, elem in list(elements.items()):
        if elem.type == "Parameter":
            if "owningNode" in elem.references:
                elem.references["activityParameterNode"] = elem.references["owningNode"]
                del elem.references["owningNode"]
