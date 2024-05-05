from gaphas.connector import ConnectionSink, Connector
from gaphas.segment import LineSegment, Segment

from gaphor.core.modeling.event import RevertibleEvent
from gaphor.diagram.connectors import ItemTemporaryDisconnected
from gaphor.diagram.presentation import LinePresentation


@Segment.register(LinePresentation)
class PresentationSegment(LineSegment):
    def split_segment(self, segment, count=2):
        self.temporary_disconnect()
        handles, ports = super().split_segment(segment, count)
        line = self.item
        line.handle(LineSplitSegmentEvent(line, segment, count))
        return handles, ports

    def merge_segment(self, segment, count=2):
        self.temporary_disconnect()
        deleted_handles, deleted_ports = super().merge_segment(segment, count)
        line = self.item
        line.handle(LineMergeSegmentEvent(line, segment, count))
        return deleted_handles, deleted_ports

    def temporary_disconnect(self):
        # Send an event to cause a "temporary disconnect". This is the contra-signal
        # of `ItemReconnected`, sent from the PresentationConnector.reconnect_handle().
        connected = self.item
        model = self.model

        for cinfo in list(model.connections.get_connections(connected=connected)):
            model.handle(
                ItemTemporaryDisconnected(
                    cinfo.item, cinfo.handle, connected, cinfo.port
                )
            )

    def recreate_constraints(self):
        connected = self.item
        model = self.model

        for cinfo in list(model.connections.get_connections(connected=connected)):
            item = cinfo.item
            handle = cinfo.handle
            connector = Connector(item, handle, model.connections)
            sink = ConnectionSink(connected, distance=float("inf"))
            connector.connect(sink)


class LineSplitSegmentEvent(RevertibleEvent):
    def __init__(self, element, segment, count):
        super().__init__(element)
        self.segment = segment
        self.count = count

    def revert(self, target):
        segment = Segment(target, target.diagram)
        segment.merge_segment(self.segment, self.count)


class LineMergeSegmentEvent(RevertibleEvent):
    def __init__(self, element, segment, count):
        super().__init__(element)
        self.segment = segment
        self.count = count

    def revert(self, target):
        segment = Segment(target, target.diagram)
        segment.split_segment(self.segment, self.count)
