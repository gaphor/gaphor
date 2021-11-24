from gaphas.segment import LineSegment, Segment

from gaphor.core.modeling.event import RevertibeEvent
from gaphor.diagram.presentation import LinePresentation


@Segment.register(LinePresentation)
class PresentationSegment(LineSegment):
    def split_segment(self, segment, count=2):
        handles, ports = super().split_segment(segment, count)
        line = self.item
        line.handle(LineSplitSegmentEvent(line, segment, count))
        return handles, ports

    def merge_segment(self, segment, count=2):
        deleted_handles, deleted_ports = super().merge_segment(segment, count)
        line = self.item
        line.handle(LineMergeSegmentEvent(line, segment, count))
        return deleted_handles, deleted_ports


class LineSplitSegmentEvent(RevertibeEvent):
    def __init__(self, element, segment, count):
        super().__init__(element)
        self.segment = segment
        self.count = count

    def revert(self, target):
        segment = Segment(target, target.diagram)
        segment.merge_segment(self.segment, self.count)


class LineMergeSegmentEvent(RevertibeEvent):
    def __init__(self, element, segment, count):
        super().__init__(element)
        self.segment = segment
        self.count = count

    def revert(self, target):
        segment = Segment(target, target.diagram)
        segment.split_segment(self.segment, self.count)
