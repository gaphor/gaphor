from gaphas.aspect.handlemove import HandleMove
from gaphas.item import Line
from gaphas.segment import LineHandleMove

from gaphor.diagram.connectors import Connector


def connectable(line, handle, element):
    connector = Connector(element, line)
    for port in element.ports():
        allow = connector.allow(handle, port)
        if allow:
            return True
    return False


@HandleMove.register(Line)
class GrayOutLineHandleMove(LineHandleMove):
    def start_move(self, pos):
        super().start_move(pos)
        handle = self.handle
        if handle.connectable:
            line = self.item
            model = self.view.model
            selection = self.view.selection
            selection.grayed_out_items = set(
                item
                for item in model.get_all_items()
                if not connectable(line, handle, item)
            )

    def stop_move(self, pos):
        super().stop_move(pos)
        selection = self.view.selection
        selection.grayed_out_items = set()
