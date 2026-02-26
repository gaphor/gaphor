"""Report generation orchestrator.

Produces a navigable HTML report from a Gaphor model, including
SVGs with clickable overlays, a sidebar tree, and element detail views.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from gaphor.core.format import format
from gaphor.core.modeling import Base, Diagram, Presentation
from gaphor.diagram.export import escape_filename, save_svg
from gaphor.diagram.group import Root, owner, owns
from gaphor.diagram.iconname import icon_name
from gaphor.plugins.htmlreport.svg_overlay import inject_overlays
from gaphor.plugins.htmlreport.templates import (
    CSS_TEMPLATE,
    HTML_TEMPLATE,
    JS_TEMPLATE,
    VENDOR_SVG_PAN_ZOOM_PATH,
)
from gaphor.UML import uml as UML
from gaphor.UML.umlfmt import format_association_end

log = logging.getLogger(__name__)


def generate_report(factory, output_dir: str | Path) -> None:
    """Generate an HTML model report to the given directory."""
    output_dir = Path(output_dir)
    diagrams_dir = output_dir / "diagrams"
    assets_dir = output_dir / "assets"

    diagrams_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Export each diagram as SVG and inject overlays
    for diagram in factory.select(Diagram):
        filename = _diagram_filename(diagram)
        svg_path = diagrams_dir / filename
        log.info("Exporting diagram: %s -> %s", diagram.name, svg_path)
        save_svg(str(svg_path), diagram)
        inject_overlays(str(svg_path), diagram)

    # Read SVG content for embedding in model data
    svg_contents = {}
    for diagram in factory.select(Diagram):
        svg_file = diagrams_dir / _diagram_filename(diagram)
        if svg_file.exists():
            svg_contents[diagram.id] = svg_file.read_text(encoding="utf-8")

    # Build model data
    model_data = build_model_data(factory, svg_contents)

    # Write assets
    (assets_dir / "style.css").write_text(CSS_TEMPLATE, encoding="utf-8")
    (assets_dir / "report.js").write_text(JS_TEMPLATE, encoding="utf-8")
    shutil.copy2(VENDOR_SVG_PAN_ZOOM_PATH, assets_dir / "svg-pan-zoom.min.js")

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
        svg_file = f"diagrams/{_diagram_filename(diagram)}"
        diagram_subjects = list(
            {item.subject.id for item in diagram.get_all_items() if item.subject}
        )

        o = owner(diagram)
        diagrams[diagram.id] = {
            "id": diagram.id,
            "name": diagram.name or "",
            "type": diagram.diagramType or "",
            "svg_file": svg_file,
            "svg_content": svg_contents.get(diagram.id, ""),
            "owner_id": o.id if isinstance(o, Base) else None,
            "elements": diagram_subjects,
        }

    for element in factory.select():
        if isinstance(element, (Presentation, Diagram)):
            continue

        el_info = extract_element_info(element)
        if el_info:
            elements[element.id] = el_info

    tree = build_tree(factory)

    return {
        "elements": elements,
        "diagrams": diagrams,
        "tree": tree,
    }


def extract_element_info(element) -> dict | None:
    """Extract properties from a model element."""
    try:
        formatted = format(element)
    except TypeError:
        formatted = ""

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

    o = owner(element)
    owner_id = o.id if isinstance(o, Base) else None

    return {
        "id": element.id,
        "name": name,
        "type": el_type,
        "formatted": formatted,
        "owner_id": owner_id,
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
    if not hasattr(element, attr_name):
        return []
    result = []
    for member in getattr(element, attr_name):
        try:
            result.append(format(member))
        except TypeError:
            result.append(member.name or "")
    return result


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
    return [
        c.name or ""
        for inst in element.appliedStereotype
        if inst.classifier
        for c in inst.classifier
    ]


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
    named = [c for c in children_elements if _has_name(c)]
    unnamed = [c for c in children_elements if not _has_name(c)]

    children = [_build_tree_node(c) for c in named]

    # Group unnamed elements under a virtual "Relationships" node
    if unnamed:
        rel_children = [_build_tree_node(c) for c in unnamed]
        children.append(
            {
                "id": f"_rels_{element.id}",
                "name": "Relationships",
                "node_type": "group",
                "icon": "gaphor-relationship",
                "children": rel_children,
            }
        )

    return {
        "id": element.id,
        "name": name,
        "node_type": node_type,
        "icon": icon_name(element),
        "children": children,
    }


def _has_name(element) -> bool:
    """Check if an element has a meaningful display name.

    Elements without a name or formatted representation (like unnamed
    ControlFlows, InitialNodes, etc.) are considered unnamed and will
    be grouped under a "Relationships" node in the tree.
    """
    if isinstance(element, Diagram):
        return True
    if getattr(element, "name", None):
        return True
    try:
        if format(element):
            return True
    except TypeError:
        pass
    return False


def _element_display_name(element) -> str:
    """Get a display name for an element."""
    if isinstance(element, Diagram):
        try:
            return format(element) or "(unnamed)"
        except TypeError:
            return element.name or "(unnamed)"

    name = getattr(element, "name", None)
    if name:
        return str(name)

    try:
        formatted = format(element)
        if formatted:
            return formatted
    except TypeError:
        pass

    return f"({type(element).__name__})"


def _tree_sort_key(element):
    """Sort key: Diagrams first, then alphabetically."""
    is_diagram = isinstance(element, Diagram)
    name = _element_display_name(element).casefold()
    return (0 if is_diagram else 1, name)
