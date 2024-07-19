from pytest_archon import archrule

import gaphor
from gaphor.entrypoint import load_entry_points

GAPHOR_CORE = [
    "gaphor.core*",
    "gaphor.abc",
    "gaphor.action",
    "gaphor.entrypoint",
    "gaphor.i18n",
    "gaphor.transaction",
    "gaphor.event",
    "gaphor.settings",
]

GLIB = [
    "gi.repository.GLib",
    "gi.repository.Gio",
]

# Pango is used for text rendering in diagrams
PANGO = [
    "gi.repository.Pango",
    "gi.repository.PangoCairo",
]

UI_LIBRARIES = [
    "gi.repository.Adw",
    "gi.repository.Gdk",
    "gi.repository.Gtk",
    "gi.repository.GObject",
]


def test_core_packages():
    (
        archrule("gaphor.core does not depend on the rest of the system")
        .match("gaphor.core*")
        .exclude("*.tests.*")
        .may_import(*GAPHOR_CORE)
        .should_not_import("gaphor*")
        .should_not_import("gi*")
        .check(gaphor, skip_type_checking=True)
    )


def test_diagram_package():
    # NB1. gaphor.diagram.tools.dropzone includes gaphor.UML.recipes,
    # so it can assign the right owner package to a newly created element.
    # NB2. The image property page requires a file dialog and some error
    # handling. Unfortunately this is UI code, so we need it from there.
    (
        archrule("Diagrams are part of the core")
        .match("gaphor.diagram*")
        .exclude("*.tests.*")
        .may_import(*GAPHOR_CORE)
        .may_import("gaphor.diagram*")
        .may_import("gaphor.UML.compartments")
        .may_import("gaphor.UML.recipes")
        .may_import("gaphor.UML.uml")
        .may_import("gaphor.ui.filedialog")
        .may_import("gaphor.ui.errorhandler")
        .should_not_import("gaphor*")
        .check(gaphor, skip_type_checking=True)
    )

    (
        archrule("GTK dependencies")
        .match("gaphor.diagram*")
        .exclude("*.tests.*")
        .exclude("gaphor.diagram.general.uicomponents")
        .exclude("gaphor.diagram.tools*")
        .exclude("gaphor.diagram.*editors")
        .exclude("gaphor.diagram.*propertypages")
        .may_import(*PANGO)
        .should_not_import("gi.repository*")
        .check(gaphor, skip_type_checking=True)
    )


def test_services_package():
    (
        archrule("Services only depend on core functionality")
        .match("gaphor.services*")
        .exclude("*.tests.*")
        .may_import(*GAPHOR_CORE, *GLIB)
        .may_import("gaphor.diagram*")
        .may_import("gaphor.services*")
        .should_not_import("gaphor*")
        .should_not_import("gi*")
        .check(gaphor, skip_type_checking=True)
    )


def test_storage_package():
    (
        archrule("Storage only depends on core functionality")
        .match("gaphor.storage*")
        .exclude("*.tests.*")
        .may_import(*GAPHOR_CORE, *GLIB, *PANGO)
        .may_import("gaphor.diagram*")
        .may_import("gaphor.storage*")
        .may_import("gaphor.application", "gaphor.services.componentregistry")
        .should_not_import("gaphor*")
        .should_not_import("gi*")
        .check(gaphor, skip_type_checking=True)
    )


def test_modeling_languages_should_not_depend_on_ui_package():
    (
        archrule("Modeling languages should not depend on the UI package")
        .match("gaphor.C4Model*", "gaphor.RAAML*", "gaphor.SysML*", "gaphor.UML*")
        .should_not_import("gaphor.ui*")
        .check(gaphor)
    )


def test_moduling_languages_should_initialize_without_gtk():
    modeling_languages: list[str] = [
        c.__module__ for c in load_entry_points("gaphor.modelinglanguages").values()
    ]
    assert modeling_languages

    (
        archrule("No GTK dependency for modeling languages")
        .match(*modeling_languages)
        .should_not_import(*UI_LIBRARIES)
        .check(gaphor)
    )


def test_uml_package_does_not_depend_on_other_modeling_languages():
    (
        archrule("No modeling language dependencies for UML")
        .match("gaphor.UML*")
        .exclude("*.tests.*")
        .should_not_import("gaphor.C4Model*", "gaphor.RAAML*", "gaphor.SysML*")
        .check(gaphor, only_toplevel_imports=True)
    )


def test_allow_main_application_to_configure_i18n():
    (
        archrule(
            "The main application should configure i18n, so it should not be imported anywhere yet"
        )
        .match("gaphor.__main__")
        .match("gaphor.main")
        .should_not_import("gaphor.i18n")
        .check(gaphor, only_toplevel_imports=True)
    )
