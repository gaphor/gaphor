"""For ease of creation, maintain a mapping from Element to Diagram Item."""

from typing import Dict, NamedTuple, Type, List

from gaphor.core.modeling import Element, Presentation, Diagram


class ElementRepresentationInfo(NamedTuple):
    element_cls: Type[Element]
    presentation_cls: Type[Presentation]
    diagram_cls: Type[Diagram]
    metadata: dict[str, object]


def represents(uml_element, diagram_type=Diagram, **metadata):
    """A decorator to assign a default Element type to a diagram item."""

    def wrapper(presentation):
        set_diagram_item(uml_element, diagram_type, presentation, metadata)
        return presentation

    return wrapper


_element_to_item_map: Dict[Element, List[ElementRepresentationInfo]] = {}


def closest_instance(item, options, project=lambda x: x):
    """ "Returns class from the options that is closest to the item class"""
    occurrences = [
        (
            opt,
            len(
                [
                    o
                    for o in options
                    if issubclass(project(o), project(opt))
                    and issubclass(item, project(o))
                ]
            ),
        )
        for opt in options
    ]

    _, opt = min([(count, opt) for opt, count in occurrences if count])

    return opt


def get_diagram_item(element_cls, diagram_cls):
    global _element_to_item_map

    options = _element_to_item_map.get(element_cls)
    info = closest_instance(diagram_cls, options, lambda info: info.diagram_cls)

    return info.presentation_cls


def has_diagram_item(element_class) -> bool:
    return element_class in _element_to_item_map


def diagram_item_has_element(item_class) -> bool:
    for _, presentations in _element_to_item_map.items():
        element_presentations = [
            presentation_cls for _, presentation_cls, _, _ in presentations
        ]
        if item_class in element_presentations:
            return True

    return False


def get_diagram_item_metadata(item_cls):
    metadatas = []
    for _, representations in _element_to_item_map.items():
        element_item_metadatas = [
            metadata
            for _, presentation_cls, _, metadata in representations
            if item_cls is presentation_cls
        ]
        metadatas.extend(element_item_metadatas)

    return metadatas[0] if metadatas else {}


def get_model_element(item_cls):
    elements = [
        element
        for element, representations in _element_to_item_map.items()
        if item_cls
        in [presentation_cls for _, presentation_cls, _, _ in representations]
    ]

    return elements[0] if elements else None


def set_diagram_item(element, diagram_cls, item, metadata):
    if element not in _element_to_item_map:
        _element_to_item_map[element] = []

    assert diagram_cls not in [
        diagram for _, _, diagram, _ in _element_to_item_map[element]
    ], "No duplicates"

    _element_to_item_map[element].append(
        ElementRepresentationInfo(element, item, diagram_cls, metadata)
    )
