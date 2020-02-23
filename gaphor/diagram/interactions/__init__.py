from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.diagram.interactions.interaction import InteractionItem
from gaphor.diagram.interactions.lifeline import LifelineItem
from gaphor.diagram.interactions.message import MessageItem


def _load():
    from gaphor.diagram.interactions import (
        messageconnect,
        interactionsgrouping,
        interactionspropertypages,
    )


_load()
