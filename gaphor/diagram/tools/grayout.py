from typing import Optional

from gaphas.connector import Handle
from gaphas.guide import GuidedItemHandleMoveMixin
from gaphas.handlemove import ConnectionSinkType, HandleMove, ItemHandleMove
from gaphas.item import Item, Line
from gaphas.move import Move
from gaphas.types import Pos
from gaphas.view import GtkView

from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import AttachedPresentation


def connectable(line, handle, element):
    connector = Connector(element, line)
    return any(connector.allow(handle, port) for port in element.ports())


class GrayOutLineHandleMoveMixin:

    view: GtkView
    item: Item
    handle: Handle

    def start_move(self, pos):
        super().start_move(pos)  # type: ignore[misc]
        handle = self.handle
        if handle.connectable:
            line = self.item
            model = self.view.model
            selection = self.view.selection
            selection.grayed_out_items = {
                item
                for item in model.get_all_items()
                if not (item is line or connectable(line, handle, item))
            }

    def stop_move(self, pos):
        super().stop_move(pos)  # type: ignore[misc]
        selection = self.view.selection
        selection.grayed_out_items = set()
        selection.dropzone_item = None

    def glue(
        self, pos: Pos, distance: int = ItemHandleMove.GLUE_DISTANCE
    ) -> Optional[ConnectionSinkType]:
        sink = super().glue(pos, distance)  # type: ignore[misc]
        self.view.selection.dropzone_item = sink and sink.item
        return sink

    def connect(self, pos: Pos) -> None:
        super().connect(pos)  # type: ignore[misc]
        self.view.selection.dropzone_item = None


@HandleMove.register(Line)
class GrayOutLineHandleMove(
    GrayOutLineHandleMoveMixin, GuidedItemHandleMoveMixin, ItemHandleMove
):
    pass


@Move.register(AttachedPresentation)
def gray_out_attached_presentation_move(item, view):
    return GrayOutLineHandleMove(item, item.handles()[0], view)
