from __future__ import annotations

from io import BytesIO

from IPython.display import SVG, DisplayObject, Image

from gaphor.core.modeling import Diagram
from gaphor.diagram.export import save_png, save_svg
from gaphor.plugins.autolayout import AutoLayout
from gaphor.services.modelinglanguage import ModelingLanguageService


def auto_layout(diagram: Diagram) -> None:
    auto_layout = AutoLayout()
    auto_layout.layout(diagram)


def draw(diagram: Diagram, format="png") -> DisplayObject:
    buffer = BytesIO()
    modeling_language = ModelingLanguageService()

    if format == "svg":
        save_svg(buffer, diagram, modeling_language)
        return SVG(buffer.getvalue())
    elif format == "png":
        save_png(buffer, diagram, modeling_language)
        return Image(buffer.getvalue())
    else:
        raise ValueError(
            f"Unsupported file format {format}. Should be either svg or png"
        )
