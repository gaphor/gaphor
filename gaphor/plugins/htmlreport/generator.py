"""Report generation orchestrator.

Produces a navigable HTML report from a Gaphor model, including
SVGs with clickable overlays, a sidebar tree, and element detail views.
"""

import json
import logging
from pathlib import Path

from gaphor.core.format import format
from gaphor.core.modeling import Base, Diagram, Presentation
from gaphor.diagram.export import escape_filename, save_svg
from gaphor.diagram.group import Root, owner, owns
from gaphor.diagram.iconname import icon_name
from gaphor.plugins.htmlreport.svg_overlay import inject_overlays
from gaphor.UML import uml as UML
from gaphor.UML.recipes import get_applied_stereotypes
from gaphor.UML.umlfmt import format_association_end

log = logging.getLogger(__name__)


def generate_report(factory, output_dir: str | Path) -> None:
    """Generate an HTML model report to the given directory."""
    template_dir = Path(__file__).parent
    HTML_TEMPLATE = (template_dir / "report.html").read_text(encoding="utf-8")
    CSS_TEMPLATE = (template_dir / "report.css").read_text(encoding="utf-8")
    JS_TEMPLATE = (template_dir / "report.js").read_text(encoding="utf-8")

    output_dir = Path(output_dir)
    diagrams_dir = output_dir / "diagrams"

    diagrams_dir.mkdir(parents=True, exist_ok=True)

    # Export each diagram as SVG and inject overlays
    svg_contents = {}
    for diagram in factory.select(Diagram):
        filename = _diagram_filename(diagram)
        svg_path = diagrams_dir / filename
        log.info("Exporting diagram: %s -> %s", diagram.name, svg_path)
        save_svg(str(svg_path), diagram)
        inject_overlays(str(svg_path), diagram)
        svg_contents[diagram.id] = svg_path.read_text(encoding="utf-8")

    # Build model data
    model_data = build_model_data(factory, svg_contents)

    # Write index.html
    html = HTML_TEMPLATE.format(
        css=CSS_TEMPLATE,
        js=JS_TEMPLATE,
        model_data=json.dumps(model_data, ensure_ascii=False),
    )
    (output_dir / "index.html").write_text(html, encoding="utf-8")

    log.info("Report generated at %s", output_dir)


def _diagram_filename(diagram: Diagram) -> str:
    name = escape_filename(diagram.name) or "diagram"
    return f"{name}_{diagram.id}.svg"


def build_model_data(factory, svg_contents: dict[str, str] | None = None) -> dict:
    """Extract all model info as a JSON-serializable dict."""
    elements = {}
    diagrams = {}
    svg_contents = svg_contents or {}

    for diagram in factory.select(Diagram):
        diagram_subjects = list(
            {item.subject.id for item in diagram.get_all_items() if item.subject}
        )

        diagrams[diagram.id] = {
            "id": diagram.id,
            "name": diagram.name or "",
            "type": diagram.diagramType or "",
            "svg_content": svg_contents.get(diagram.id, ""),
            "owner_id": _owner_id(diagram),
            "elements": diagram_subjects,
        }

    for element in factory.select():
        if isinstance(element, (Presentation, Diagram)):
            continue

        elements[element.id] = extract_element_info(element)

    tree = build_tree(factory)

    return {
        "elements": elements,
        "diagrams": diagrams,
        "tree": tree,
    }


def _owner_id(element) -> str | None:
    """Return the element's owner ID, or None if owned by Root or unowned."""
    o = owner(element)
    return o.id if isinstance(o, Base) else None


def _format_safe(element, default: str = "") -> str:
    """Format an element, returning default if no formatter is registered."""
    try:
        return format(element) or default
    except TypeError:
        return default


def extract_element_info(element) -> dict:
    """Extract properties from a model element."""
    formatted = _format_safe(element)

    name = getattr(element, "name", "") or ""
    el_type = type(element).__name__

    # Find diagrams this element appears in
    el_diagrams = []
    if hasattr(element, "presentation"):
        seen = set()
        for pres in element.presentation:
            if pres.diagram and pres.diagram.id not in seen:
                seen.add(pres.diagram.id)
                el_diagrams.append(
                    {"id": pres.diagram.id, "name": pres.diagram.name or ""}
                )

    return {
        "id": element.id,
        "name": name,
        "type": el_type,
        "formatted": formatted,
        "owner_id": _owner_id(element),
        "diagrams": el_diagrams,
        "properties": _extract_properties(element),
        "attributes": _extract_formatted_members(element, "ownedAttribute"),
        "operations": _extract_formatted_members(element, "ownedOperation"),
        "literals": _extract_literals(element),
        "associations": _extract_associations(element),
        "generalizations": _extract_generalizations(element),
        "stereotypes": _extract_stereotypes(element),
    }


def _extract_properties(element) -> list[dict]:
    """Extract common boolean/enum properties from an element."""
    properties = []
    for attr_name in (
        "visibility",
        "isAbstract",
        "isLeaf",
        "isFinalSpecialization",
        "isDerived",
        "isReadOnly",
        "isStatic",
        "isOrdered",
        "isUnique",
        "isActive",
    ):
        if hasattr(element, attr_name):
            val = getattr(element, attr_name)
            if val is not None and val is not False:
                properties.append({"name": attr_name, "value": str(val)})
    return properties


def _extract_formatted_members(element, attr_name: str) -> list[str]:
    """Extract and format owned members (attributes or operations)."""
    members = getattr(element, attr_name, None)
    if members is None:
        return []
    return [_format_safe(m, m.name or "") for m in members]


def _extract_literals(element) -> list[str]:
    """Extract enumeration literals."""
    if not isinstance(element, UML.Enumeration):
        return []
    return [lit.name or "" for lit in element.ownedLiteral]


def _extract_associations(element) -> list[dict]:
    """Extract association end information."""
    associations = []
    if isinstance(element, UML.Association):
        for end in element.memberEnd:
            end_name, end_mult = format_association_end(end)
            associations.append(
                {
                    "name": end_name,
                    "multiplicity": end_mult,
                    "type": end.type.name if end.type else "",
                    "aggregation": end.aggregation or "none",
                    "navigable": end in element.navigableOwnedEnd,
                }
            )
    return associations


def _extract_generalizations(element) -> list[dict]:
    """Extract generalizations (superclasses/interfaces)."""
    generalizations = []
    if hasattr(element, "generalization"):
        for gen in element.generalization:
            if gen.general:
                generalizations.append(
                    {
                        "id": gen.general.id,
                        "name": gen.general.name or "",
                        "type": type(gen.general).__name__,
                    }
                )
    return generalizations


def _extract_stereotypes(element) -> list[str]:
    """Extract applied stereotype names."""
    if not hasattr(element, "appliedStereotype"):
        return []
    return [st.name or "" for st in get_applied_stereotypes(element)]


_ICON_FA_CLASSES = {
    # Diagrams
    "gaphor-diagram-symbolic": "fa-solid fa-image",
    # Structure
    "gaphor-package-symbolic": "fa-solid fa-box",
    "gaphor-profile-symbolic": "fa-solid fa-box",
    "gaphor-class-symbolic": "fa-solid fa-c",
    "gaphor-metaclass-symbolic": "fa-solid fa-m",
    "gaphor-interface-symbolic": "fa-regular fa-circle",
    "gaphor-component-symbolic": "fa-solid fa-puzzle-piece",
    "gaphor-enumeration-symbolic": "fa-solid fa-list-ol",
    "gaphor-data-type-symbolic": "fa-solid fa-hashtag",
    "gaphor-primitive-type-symbolic": "fa-solid fa-hashtag",
    "gaphor-artifact-symbolic": "fa-regular fa-file",
    "gaphor-node-symbolic": "fa-solid fa-server",
    "gaphor-device-symbolic": "fa-solid fa-desktop",
    # Behavior
    "gaphor-actor-symbolic": "fa-solid fa-user",
    "gaphor-use-case-symbolic": "fa-regular fa-circle-dot",
    "gaphor-activity-symbolic": "fa-solid fa-play",
    "gaphor-state-machine-symbolic": "fa-solid fa-diagram-project",
    "gaphor-state-symbolic": "fa-regular fa-circle",
    "gaphor-region-symbolic": "fa-solid fa-layer-group",
    "gaphor-transition-symbolic": "fa-solid fa-arrow-right",
    "gaphor-interaction-symbolic": "fa-solid fa-arrows-left-right",
    "gaphor-signal-symbolic": "fa-solid fa-bolt",
    # Relationships
    "gaphor-association-symbolic": "fa-solid fa-link",
    "gaphor-dependency-symbolic": "fa-solid fa-arrow-right",
    "gaphor-generalization-symbolic": "fa-solid fa-arrow-up",
    "gaphor-realization-symbolic": "fa-solid fa-arrow-up",
    # Properties and features
    "gaphor-property-symbolic": "fa-solid fa-circle-info",
    "gaphor-operation-symbolic": "fa-solid fa-gear",
    "gaphor-port-symbolic": "fa-solid fa-plug",
    "gaphor-connector-symbolic": "fa-solid fa-minus",
    # Profiles and constraints
    "gaphor-stereotype-symbolic": "fa-solid fa-tag",
    "gaphor-constraint-symbolic": "fa-solid fa-code",
    "gaphor-comment-symbolic": "fa-regular fa-comment",
    "gaphor-collaboration-symbolic": "fa-solid fa-people-group",
    "gaphor-information-flow-symbolic": "fa-solid fa-right-long",
    # SysML
    "gaphor-block-symbolic": "fa-solid fa-square",
    "gaphor-requirement-symbolic": "fa-solid fa-check",
    "gaphor-value-type-symbolic": "fa-solid fa-hashtag",
    "gaphor-constraint-block-symbolic": "fa-solid fa-code",
    "gaphor-interface-block-symbolic": "fa-regular fa-circle",
    # C4 Model
    "gaphor-c4-software-system-symbolic": "fa-solid fa-building",
    "gaphor-c4-container-symbolic": "fa-solid fa-box",
    "gaphor-c4-component-symbolic": "fa-solid fa-puzzle-piece",
    "gaphor-c4-database-symbolic": "fa-solid fa-database",
    "gaphor-c4-person-symbolic": "fa-solid fa-user",
    # Virtual group node
    "gaphor-relationship": "fa-solid fa-folder",
}

_DEFAULT_ICON_FA_CLASS = "fa-solid fa-circle"


def _icon_fa_class(element) -> str:
    """Map a Gaphor element to its Font Awesome icon class."""
    return _ICON_FA_CLASSES.get(icon_name(element), _DEFAULT_ICON_FA_CLASS)


def build_tree(factory) -> list[dict]:
    """Build a hierarchical tree structure for the sidebar."""
    roots = [
        e
        for e in factory.select()
        if not isinstance(e, Presentation) and owner(e) is Root
    ]
    roots.sort(key=_tree_sort_key)
    return [_build_tree_node(e) for e in roots]


def _build_tree_node(element) -> dict:
    """Build a single tree node with children."""
    name = _element_display_name(element)
    node_type = "diagram" if isinstance(element, Diagram) else "element"

    children_elements = owns(element)
    # Filter out Presentation items from children
    children_elements = [
        c for c in children_elements if not isinstance(c, Presentation)
    ]
    children_elements.sort(key=_tree_sort_key)

    # Split into named and unnamed (relationships etc.)
    named = [c for c in children_elements if not isinstance(c, UML.Relationship)]
    unnamed = [c for c in children_elements if isinstance(c, UML.Relationship)]

    children = [_build_tree_node(c) for c in named]

    # Group unnamed elements under a virtual "Relationships" node
    if unnamed:
        rel_children = [_build_tree_node(c) for c in unnamed]
        children.append(
            {
                "id": f"_rels_{element.id}",
                "name": "Relationships",
                "node_type": "group",
                "icon": _ICON_FA_CLASSES.get(
                    "gaphor-relationship", _DEFAULT_ICON_FA_CLASS
                ),
                "children": rel_children,
            }
        )

    return {
        "id": element.id,
        "name": name,
        "node_type": node_type,
        "icon": _icon_fa_class(element),
        "children": children,
    }


def _element_display_name(element) -> str:
    """Get a display name for an element."""
    if isinstance(element, Diagram):
        return _format_safe(element) or element.name or "(unnamed)"

    name = getattr(element, "name", None)
    if name:
        return str(name)

    return _format_safe(element) or f"({type(element).__name__})"


def _tree_sort_key(element):
    """Sort key: Diagrams first, then alphabetically."""
    is_diagram = isinstance(element, Diagram)
    name = _element_display_name(element).casefold()
    return (0 if is_diagram else 1, name)
