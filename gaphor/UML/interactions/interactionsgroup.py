from gaphor.diagram.group import group, no_group
from gaphor.UML.uml import Interaction, Lifeline, Message, Type


@group.register(Interaction, Lifeline)
def interaction_lifeline_group(parent, element):
    """Add lifeline to interaction."""
    element.interaction = parent
    return True


@group.register(Interaction, Message)
def interaction_message_group(parent, element):
    """Add message to interaction."""
    element.interaction = parent
    return True


group.register(Interaction, Type)(no_group)
