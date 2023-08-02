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

"""
from gaphor.UML.interactions.lifeline import LifetimeItem
from gaphor.UML.interactions.executionspecification import ExecutioSpecificationItem


HandleMove.register(ExecutionSpecificationItem, StickyAttachedHandleMove)
Move.register(ExecutionSpecificationItem, sticky_attached_move)

HandleMove.register(LifetimeItem, StickyAttachedHandleMove)
Move.register(LifetimeItem, sticky_attached_move)
"""
