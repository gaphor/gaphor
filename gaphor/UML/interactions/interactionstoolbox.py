"""The definition for the interactions section of the toolbox."""

from gaphas.item import SE
from gaphas.segment import Segment

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.UML import diagramitems
from gaphor.UML.recipes import owner_package
from gaphor.UML.toolboxconfig import namespace_config


def interaction_config(new_item):
    subject = new_item.subject
    subject.name = new_item.diagram.gettext("New {name}").format(
        name=new_item.diagram.gettext(type(subject).__name__)
    )
    if subject.interaction:
        return

    diagram = new_item.diagram
    package = owner_package(diagram.owner)

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
        interaction.name = new_item.diagram.gettext("Interaction")
        interaction.package = package

    subject.interaction = interaction


def reflexive_message_config(new_item):
    Segment(new_item, new_item.diagram).split_segment(0, count=3)

    new_item.handles()[1].pos = (40, 0)
    new_item.handles()[2].pos = (40, 20)
    new_item.handles()[-1].pos = (0, 20)
    new_item.horizontal = True
    new_item.orthogonal = True


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
            handle_index=-1,
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
        ToolDef(
            "toolbox-reflexive-message",
            gettext("Reflexive message"),
            "gaphor-reflexive-message-symbolic",
            None,
            new_item_factory(
                diagramitems.MessageItem, config_func=reflexive_message_config
            ),
        ),
    ),
)
