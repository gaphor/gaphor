import pytest
from gaphas.canvas import Canvas, Context, instant_cairo_context
from gaphas.view import Context

from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.UML import Diagram


def test_draw_on_canvas():
    canvas = Canvas()
    execSpec = ExecutionSpecificationItem()
    canvas.add(execSpec)
    cr = instant_cairo_context()
    execSpec.draw(Context(cairo=cr))
