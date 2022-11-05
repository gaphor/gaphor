from gaphas.handlemove import HandleMove, ItemHandleMove
from gaphas.tool import item_tool as _item_tool
from gaphas.types import Pos
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.core.modeling import Presentation
from gaphor.diagram.connectors import ItemTemporaryDisconnected
from gaphor.diagram.presentation import LinePresentation


def item_tool(view: GtkView) -> Gtk.GestureDrag:
    gesture = _item_tool(view)
    gesture.connect_after("drag-end", on_drag_end)
    return gesture


def on_drag_end(gesture, _offset_x, _offset_y):
    view = gesture.get_widget()
    view.selection.dropzone_item = None


@HandleMove.register(Presentation)
@HandleMove.register(LinePresentation)
class PresentationHandleMove(ItemHandleMove):
    def start_move(self, pos: Pos) -> None:
        super().start_move(pos)
        model = self.view.model
        assert model
        if cinfo := model.connections.get_connection(self.handle):
            self.item.handle(
                ItemTemporaryDisconnected(
                    cinfo.item, cinfo.handle, cinfo.connected, cinfo.port
                )
            )
