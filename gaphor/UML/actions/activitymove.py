from gaphas.handlemove import HandleMove
from gaphas.move import Move

from gaphor.diagram.tools.handlemove import (
    StickyAttachedHandleMove,
    sticky_attached_move,
)
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.actions.pin import PinItem

HandleMove.register(ActivityParameterNodeItem, StickyAttachedHandleMove)
Move.register(ActivityParameterNodeItem, sticky_attached_move)

HandleMove.register(PinItem, StickyAttachedHandleMove)
Move.register(PinItem, sticky_attached_move)
