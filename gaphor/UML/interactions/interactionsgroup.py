from gaphor.diagram.group import group
from gaphor.UML.uml import Interaction, Lifeline, Message, Type


@group.register(Interaction, Lifeline)
def interaction_lifeline_group(parent, element):
    """Add lifeline to interaction."""
    parent.lifeline = element
    return True


@group.register(Interaction, Message)
def interaction_message_group(parent, element):
    """Add message to interaction."""
    parent.message = element
    return True


@group.register(Interaction, Type)
def not_any_type(parent, element):
    return False
