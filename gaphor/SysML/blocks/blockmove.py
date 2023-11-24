from gaphas.handlemove import HandleMove
from gaphas.move import Move

from gaphor.diagram.tools.handlemove import (
    StickyAttachedHandleMove,
    sticky_attached_move,
)
from gaphor.SysML.blocks.proxyport import ProxyPortItem

HandleMove.register(ProxyPortItem, StickyAttachedHandleMove)
Move.register(ProxyPortItem, sticky_attached_move)
