from gaphor.UML.interactions.executionspecification import ExecutionSpecificationItem
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


def _load():
    from gaphor.UML.interactions import (
        interactionsconnect,
        interactionsgrouping,
        interactionspropertypages,
    )


_load()
