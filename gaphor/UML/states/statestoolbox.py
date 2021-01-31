"""The definition for the states section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.UML import diagramitems


def initial_pseudostate_config(new_item):
    new_item.subject.kind = "initial"
    state_machine_config(new_item)


def history_pseudostate_config(new_item):
    new_item.subject.kind = "shallowHistory"
    state_machine_config(new_item)


def state_machine_config(new_item):
    subject = new_item.subject
    subject.name = f"New{type(subject).__name__}"
    if subject.container:
        return

    diagram = new_item.diagram
    package = diagram.namespace

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
        state_machine.name = "StateMachine"
        state_machine.package = package

    if state_machine.region:
        region = state_machine.region[0]
    else:
        region = subject.model.create(UML.Region)
        region.name = "DefaultRegion"
        region.stateMachine = state_machine

    subject.container = region


states = ToolSection(
    gettext("States"),
    (
        ToolDef(
            "toolbox-state",
            gettext("State"),
            "gaphor-state-symbolic",
            "s",
            new_item_factory(
                diagramitems.StateItem, UML.State, config_func=state_machine_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-initial-pseudostate",
            gettext("Initial Pseudostate"),
            "gaphor-initial-pseudostate-symbolic",
            "<Shift>S",
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                initial_pseudostate_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-final-state",
            gettext("Final State"),
            "gaphor-final-state-symbolic",
            "x",
            new_item_factory(
                diagramitems.FinalStateItem,
                UML.FinalState,
                config_func=state_machine_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-history-pseudostate",
            gettext("History Pseudostate"),
            "gaphor-pseudostate-symbolic",
            "q",
            new_item_factory(
                diagramitems.PseudostateItem,
                UML.Pseudostate,
                history_pseudostate_config,
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
    ),
)
