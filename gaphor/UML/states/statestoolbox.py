"""The definition for the states section of the toolbox."""

from functools import partial

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.UML import diagramitems
from gaphor.UML.recipes import owner_package
from gaphor.UML.toolboxconfig import namespace_config


def state_config(new_item):
    state_machine_config(new_item, name=new_item.diagram.gettext("State"))


def pseudostate_config(new_item, kind):
    new_item.subject.kind = kind
    state_machine_config(new_item)


def state_machine_config(new_item, name=None):
    subject = new_item.subject
    if name:
        subject.name = new_item.diagram.gettext("New {name}").format(name=name)
    if subject.container:
        return

    diagram = new_item.diagram
    package = owner_package(diagram.owner)

    state_machines = (
        [i for i in package.ownedType if isinstance(i, UML.StateMachine)]
        if package
        else diagram.model.lselect(
            lambda e: isinstance(e, UML.StateMachine) and e.package is None
        )
    )

    if state_machines:
        state_machine = state_machines[0]
    else:
        state_machine = subject.model.create(UML.StateMachine)
        state_machine.name = new_item.diagram.gettext("State Machine")
        state_machine.package = package

    if state_machine.region:
        region = state_machine.region[0]
    else:
        region = subject.model.create(UML.Region)
        region.stateMachine = state_machine

    subject.container = region


states = ToolSection(
    gettext("States"),
    (
        ToolDef(
            "toolbox-state-machine",
            gettext("State Machine"),
            "gaphor-state-machine-symbolic",
            None,
            new_item_factory(
                diagramitems.StateMachineItem,
                UML.StateMachine,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-state",
            gettext("State"),
            "gaphor-state-symbolic",
            "s",
            new_item_factory(
                diagramitems.StateItem,
                UML.State,
                config_func=state_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-initial-pseudostate",
            gettext("Initial Pseudostate"),
            "gaphor-initial-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="initial"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-final-state",
            gettext("Final State"),
            "gaphor-final-state-symbolic",
            None,
            new_item_factory(
                diagramitems.FinalStateItem,
                UML.FinalState,
                config_func=state_machine_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-transition",
            gettext("Transition"),
            "gaphor-transition-symbolic",
            "<Shift>T",
            new_item_factory(diagramitems.TransitionItem),
        ),
        ToolDef(
            "toolbox-shallow-history-pseudostate",
            gettext("Shallow History Pseudostate"),
            "gaphor-shallow-history-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="shallowHistory"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-deep-history-pseudostate",
            gettext("Deep History Pseudostate"),
            "gaphor-deep-history-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="deepHistory"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-join-pseudostate",
            gettext("Join Pseudostate"),
            "gaphor-join-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="join"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-fork-pseudostate",
            gettext("Fork Pseudostate"),
            "gaphor-fork-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="fork"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-junction-pseudostate",
            gettext("Junction Pseudostate"),
            "gaphor-junction-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="junction"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-choice-pseudostate",
            gettext("Choice Pseudostate"),
            "gaphor-choice-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="choice"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-entry-point-pseudostate",
            gettext("Entry Point Pseudostate"),
            "gaphor-entry-point-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="entryPoint"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-exit-point-pseudostate",
            gettext("Exit Point Pseudostate"),
            "gaphor-exit-point-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="exitPoint"),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-terminate-pseudostate",
            gettext("Terminate Pseudostate"),
            "gaphor-terminate-pseudostate-symbolic",
            None,
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                partial(pseudostate_config, kind="terminate"),
            ),
            handle_index=SE,
        ),
    ),
)
