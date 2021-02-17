"""The definition for the interactions section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, namespace_config
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.UML import diagramitems


def interaction_config(new_item):
    subject = new_item.subject
    subject.name = f"New{type(subject).__name__}"
    if subject.interaction:
        return

    diagram = new_item.diagram
    package = diagram.namespace

    interactions = (
        [i for i in package.ownedType if isinstance(i, UML.Interaction)]
        if package
        else diagram.model.lselect(
            lambda e: isinstance(e, UML.Interaction) and e.package is None
        )
    )
    if interactions:
        interaction = interactions[0]
    else:
        interaction = subject.model.create(UML.Interaction)
        interaction.name = "Interaction"
        interaction.package = package

    subject.interaction = interaction


interactions = ToolSection(
    gettext("Interactions"),
    (
        ToolDef(
            "toolbox-interaction",
            gettext("Interaction"),
            "gaphor-interaction-symbolic",
            "<Shift>N",
            new_item_factory(
                diagramitems.InteractionItem,
                UML.Interaction,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-lifeline",
            gettext("Lifeline"),
            "gaphor-lifeline-symbolic",
            "v",
            new_item_factory(
                diagramitems.LifelineItem,
                UML.Lifeline,
                config_func=interaction_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-execution-specification",
            gettext("Execution Specification"),
            "gaphor-execution-specification-symbolic",
            None,
            new_item_factory(diagramitems.ExecutionSpecificationItem),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-message",
            gettext("Message"),
            "gaphor-message-symbolic",
            "M",
            new_item_factory(diagramitems.MessageItem),
        ),
    ),
)
