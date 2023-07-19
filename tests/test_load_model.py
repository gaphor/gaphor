"""Diagram could not be loaded due to JuggleError (presumed cyclic resolving of
diagram items)."""


from gaphor import UML
from gaphor.storage.storage import load
from gaphor.UML.classes.association import (
    draw_head_navigable,
    draw_tail_composite,
    draw_tail_shared,
)


def test_association_ends_are_set(element_factory, modeling_language, test_models):
    with (test_models / "association-ends.gaphor").open(encoding="utf-8") as file_obj:
        load(file_obj, element_factory, modeling_language)
    composite = next(
        element_factory.select(
            lambda e: isinstance(e, UML.Association) and e.name == "composite"
        )
    )
    shared = next(
        element_factory.select(
            lambda e: isinstance(e, UML.Association) and e.name == "shared"
        )
    )

    assert composite.presentation[0].draw_head is draw_head_navigable
    assert composite.presentation[0].draw_tail is draw_tail_composite
    assert shared.presentation[0].draw_head is draw_head_navigable
    assert shared.presentation[0].draw_tail is draw_tail_shared
