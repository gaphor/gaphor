from __future__ import annotations

from io import BytesIO

import cairo
from IPython.display import SVG

from gaphor.core.modeling import Diagram
from gaphor.diagram.export import render
from gaphor.plugins.autolayout import AutoLayout


def auto_layout(diagram: Diagram) -> None:
    auto_layout = AutoLayout()
    auto_layout.layout(diagram)


def draw(diagram: Diagram) -> SVG:
    buffer = BytesIO()
    surface = render(diagram, lambda w, h: cairo.SVGSurface(buffer, w, h))
    surface.flush()
    surface.finish()
    return SVG(buffer.getvalue())
