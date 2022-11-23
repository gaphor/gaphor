from pytest_archon import archrule

import gaphor

GAHOR_CORE = [
    "gaphor.core*",
    "gaphor.abc",
    "gaphor.action",
    "gaphor.i18n",
    "gaphor.transaction",
    "gaphor.event",
]


def test_core_packages():
    (
        archrule("gaphor.core does not depend on the rest of the system")
        .match("gaphor.core*")
        .exclude("*.tests.*")
        .may_import(*GAHOR_CORE)
        .should_not_import("gaphor*")
        .check(gaphor, skip_type_checking=True)
    )


def test_diagram_package():
    # NB. gaphor.diagram.tools.dropzone includes gaphor.UML.recipes,
    # so it can assign the right owner package to a newly created element.
    (
        archrule("Diagrams are part of the core")
        .match("gaphor.diagram*")
        .exclude("*.tests.*")
        .may_import(*GAHOR_CORE)
        .may_import("gaphor.diagram*")
        .may_import("gaphor.UML.recipes")
        .may_import("gaphor.UML.uml")
        .should_not_import("gaphor*")
        .check(gaphor)
    )


def test_modeling_languages_do_not_depend_on_ui_package():
    (
        archrule("Modeling languages should not depend on the UI package")
        .match("gaphor.C4Model*", "gaphor.RAAML*", "gaphor.SysML*", "gaphor.UML*")
        .should_not_import("gaphor.ui*")
        .check(gaphor)
    )


def test_uml_package_does_not_depend_on_other_modeling_languages():
    (
        archrule("Modeling languages should not depend on the UI package")
        .match("gaphor.UML*")
        .exclude("*.tests.*")
        .should_not_import("gaphor.C4Model*", "gaphor.RAAML*", "gaphor.SysML*")
        .check(gaphor, only_toplevel_imports=True)
    )
