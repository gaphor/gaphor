"""Support code for dealing with stereotypes in diagrams."""

from gaphor.core.format import format
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, CssNode, Text, draw_top_separator


def stereotype_watches(
    presentation: ElementPresentation, base="subject[UML:Element]"
) -> None:
    presentation.watch(f"{base}.appliedStereotype", presentation.update_shapes).watch(
        f"{base}.appliedStereotype.classifier.name"
    ).watch(f"{base}.appliedStereotype.slot", presentation.update_shapes).watch(
        f"{base}.appliedStereotype.slot.definingFeature.name"
    ).watch(f"{base}.appliedStereotype.slot.value", presentation.update_shapes)


def stereotype_compartments(subject):
    return filter(
        None,
        (
            _create_stereotype_compartment(appliedStereotype)
            for appliedStereotype in subject.appliedStereotype
        )
        if subject
        else [],
    )


def _create_stereotype_compartment(appliedStereotype):
    def lazy_format(slot):
        return lambda: format(slot)

    slots = [slot for slot in appliedStereotype.slot if slot.value]

    if slots:
        return CssNode(
            "compartment",
            appliedStereotype,
            Box(
                CssNode(
                    "heading",
                    appliedStereotype.classifier,
                    Text(
                        text=lazy_format(appliedStereotype.classifier[0])
                        if appliedStereotype.classifier
                        else "",
                    ),
                ),
                *(
                    CssNode(
                        "slot",
                        slot,
                        Text(
                            text=lazy_format(slot),
                        ),
                    )
                    for slot in slots
                ),
                draw=draw_top_separator,
            ),
        )
    return None
