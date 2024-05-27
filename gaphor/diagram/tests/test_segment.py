from gaphas.segment import Segment

from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.segment import PresentationSegment


def test_presentation_segment_is_selected(diagram):
    line = diagram.create(LinePresentation)

    segment = Segment(line, diagram)

    assert isinstance(segment, PresentationSegment)
