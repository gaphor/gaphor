# flake8: noqa F401,F811
"""Diagram could not be loaded due to JuggleError (presumed cyclic resolving of
diagram items)."""

from gi.repository import GLib, Gtk

from gaphor import UML
from gaphor.diagram.tests.fixtures import (
    element_factory,
    event_manager,
    modeling_language,
)
from gaphor.storage.storage import load
from gaphor.UML.classes.association import (
    draw_head_navigable,
    draw_tail_composite,
    draw_tail_shared,
)


def test_cyclic_diagram_bug(element_factory, modeling_language, test_models):
    """Load file.

    This does not nearly resemble the error, since the model should be
    loaded from within the mainloop (which will delay all updates).
    """
    path = test_models / "dbus.gaphor"
    load(path, element_factory, modeling_language)


def test_cyclic_diagram_bug_idle(element_factory, modeling_language, test_models):
    """Load file in gtk main loop.

    This does not nearly resemble the error, since the model should be
    loaded from within the mainloop (which will delay all updates).
    """

    def handler():
        try:
            path = test_models / "dbus.gaphor"
            load(path, element_factory, modeling_language)
        finally:
            Gtk.main_quit()

    assert GLib.timeout_add(1, handler) > 0

    ctx = GLib.main_context_default()
    while ctx.pending():
        ctx.iteration(False)


def test_association_ends_are_set(element_factory, modeling_language, test_models):
    load(test_models / "association-ends.gaphor", element_factory, modeling_language)
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
