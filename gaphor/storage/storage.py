"""Load and save Gaphor models to Gaphors own XML format.

Three functions are exported: `load(file_obj)`loads a model from a
file. `save(file_obj)` stores the current model in a file.
"""

__all__ = ["load", "save"]

import io
import logging
from functools import partial
from typing import Callable, Iterable

from gaphor import application
from gaphor.core.modeling import Diagram, Element, ElementFactory, Presentation
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.modelinglanguage import ModelingLanguage
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.storage.parser import GaphorLoader, element, parse_generator
from gaphor.storage.xmlwriter import XMLWriter

FILE_FORMAT_VERSION = "3.0"
NAMESPACE_MODEL = "http://gaphor.sourceforge.net/model"

log = logging.getLogger(__name__)


def save(out=None, element_factory=None, status_queue=None):
    for status in save_generator(out, element_factory):
        if status_queue:
            status_queue(status)


def save_generator(out, element_factory):
    """Save the current model using @writer, which is a
    gaphor.storage.xmlwriter.XMLWriter instance."""

    writer = XMLWriter(out)
    writer.startDocument()
    writer.startPrefixMapping("", NAMESPACE_MODEL)
    writer.startElementNS(
        (NAMESPACE_MODEL, "gaphor"),
        None,
        {
            (NAMESPACE_MODEL, "version"): FILE_FORMAT_VERSION,
            (NAMESPACE_MODEL, "gaphor-version"): application.distribution().version,
        },
    )

    size = element_factory.size()
    save_func = partial(save_element, element_factory=element_factory, writer=writer)
    for n, e in enumerate(element_factory.values(), start=1):
        clazz = e.__class__.__name__
        assert e.id
        writer.startElement(clazz, {"id": str(e.id)})
        e.save(save_func)
        writer.endElement(clazz)

        if n % 25 == 0:
            yield (n * 100) / size

    writer.endElementNS((NAMESPACE_MODEL, "gaphor"), None)
    writer.endPrefixMapping("")
    writer.endDocument()


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
            writer.startElement(name, {})
            writer.startElement("ref", {"refid": value.id})
            writer.endElement("ref")
            writer.endElement(name)

    def save_collection(name, value):
        """Save a list of references."""
        if value:
            writer.startElement(name, {})
            writer.startElement("reflist", {})
            for v in value:
                if resolvable(v):
                    writer.startElement("ref", {"refid": v.id})
                    writer.endElement("ref")
            writer.endElement("reflist")
            writer.endElement(name)

    def save_value(name, value):
        """Save a value (attribute)."""
        if value is not None:
            writer.startElement(name, {})
            writer.startElement("val", {})
            if isinstance(value, bool):
                # Write booleans as 0/1.
                writer.characters(str(int(value)))
            else:
                writer.characters(str(value))
            writer.endElement("val")
            writer.endElement(name)

    if isinstance(value, Element):
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

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    yield from _load_elements_and_canvasitems(
        elements,
        element_factory,
        modeling_language,
        gaphor_version,
        update_status_queue,
    )
    yield from _load_attributes_and_references(elements, update_status_queue)

    upgrade_ensure_style_sheet_is_present(element_factory)

    for _id, elem in list(elements.items()):
        yield from update_status_queue()
        assert elem.element
        elem.element.postload()

    for diagram in element_factory.select(Diagram):
        diagram.update()


def _load_elements_and_canvasitems(
    elements: dict[str, element],
    element_factory: ElementFactory,
    modeling_language: ModelingLanguage,
    gaphor_version: str,
    update_status_queue: Callable[[], Iterable[float]],
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
        if not (cls := modeling_language.lookup_element(elem.type)):
            raise UnknownModelElementError(
                f"Type {elem.type} cannot be loaded: no such element"
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
            if subject.values.get("note"):
                subject.values["note"] += "\n\n" + elem.values["note"]
            else:
                subject.values["note"] = elem.values["note"]
            del elem.values["note"]
    return elem
