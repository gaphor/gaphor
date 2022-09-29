from gaphas.segment import Segment

from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.general.simpleitem import Line
from gaphor.diagram.tests.fixtures import connect


def test_expose_merge_issue(diagram):
    line = diagram.create(Line)
    segment = Segment(line, diagram)
    segment.split_segment(0)

    comment_line = diagram.create(CommentLineItem)
    connect(comment_line, comment_line.head, line, line.ports()[1])

    segment.merge_segment(0)

    diagram.unlink()
