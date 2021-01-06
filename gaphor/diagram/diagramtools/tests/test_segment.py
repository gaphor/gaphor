from gaphas.segment import Segment

from gaphor.diagram.diagramtools.segment import PresentationSegment
from gaphor.diagram.presentation import LinePresentation


def test_presentation_segment_is_selected(diagram):
    line = diagram.create(LinePresentation)

    segment = Segment(line, diagram)

    assert isinstance(segment, PresentationSegment)
