from .interaction import InteractionItem
from .message import MessageItem
from .lifeline import LifelineItem


def _load():
    from . import messageconnect, interactionsgrouping, interactionspropertypages


_load()
