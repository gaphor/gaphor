from __future__ import annotations

import operator
from typing import Iterator, Protocol, Sequence, TypedDict, Union

from gaphor.core.styling.compiler import compile_style_sheet
from gaphor.core.styling.declarations import (
    FONT_SIZE_VALUES,
    Color,
    FontStyle,
    FontWeight,
    JustifyContent,
    Number,
    Padding,
    TextAlign,
    TextDecoration,
    Var,
    VerticalAlign,
    declarations,
    number,
)

# Style is using SVG properties where possible
# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute
# NB. The Style can also contain variables (start with `--`),
#     however those are not part of the interface.
Style = TypedDict(
    "Style",
    {
        "background-color": Color,
        "border-radius": Number,
        "color": Color,
        "dash-style": Sequence[Number],
        "padding": Padding,
        "font-family": str,
        "font-size": Union[int, float, str],
        "font-style": FontStyle,
        "font-weight": FontWeight,
        "justify-content": JustifyContent,
        "line-style": Number,
        "line-width": Number,
        "min-width": Number,
        "min-height": Number,
        "opacity": Number,
        "text-decoration": TextDecoration,
        "text-align": TextAlign,
        "text-color": Color,
        "vertical-align": VerticalAlign,
        "vertical-spacing": Number,
    },
    total=False,
)


class StyleNode(Protocol):
    def name(self) -> str:
        ...

    def parent(self) -> StyleNode | None:
        ...

    def children(self) -> Iterator[StyleNode]:
        ...

    def attribute(self, name: str) -> str:
        ...

    def state(self) -> Sequence[str]:
        ...


def merge_styles(*styles: Style) -> Style:
    style = Style()
    abs_font_size = None
    for s in styles:
        font_size = s.get("font-size")
        if font_size and isinstance(font_size, number):
            abs_font_size = font_size
        style.update(s)

    if abs_font_size and style["font-size"] in FONT_SIZE_VALUES:
        style["font-size"] = abs_font_size * FONT_SIZE_VALUES[style["font-size"]]  # type: ignore[index,operator]

    if "opacity" in style:
        opacity = style["opacity"]
        for color_prop in ("color", "background-color", "text-color"):
            color: Color | None = style.get(color_prop)  # type: ignore[assignment]
            if color and color[3] > 0.0:
                style[color_prop] = color[:3] + (color[3] * opacity,)  # type: ignore[literal-required]

    return resolve_variables(style, styles)


def resolve_variables(style: Style, style_layers: Sequence[Style]) -> Style:
    new_style = Style()
    for p, v in style.items():
        if isinstance(v, Var):
            # Go through the individual layers.
            # Fall back if a variable does not resolve.
            for layer in reversed(style_layers):
                if p in layer and (lv := layer[p]):  # type: ignore[literal-required]
                    if isinstance(lv, Var):
                        if (
                            lv.name in style
                            and (
                                resolved := declarations(p, style[lv.name])  # type: ignore[literal-required]
                            )
                            and not isinstance(resolved, Var)
                        ):
                            new_style[p] = resolved  # type: ignore[literal-required]
                            break
                    else:
                        new_style[p] = lv  # type: ignore[literal-required]
                        break
        else:
            new_style[p] = v  # type: ignore[literal-required]
    return new_style


class CompiledStyleSheet:
    def __init__(self, *css: str):
        self.selectors = [
            (selspec[0], selspec[1], order, declarations)
            for order, (selspec, declarations) in enumerate(compile_style_sheet(*css))
            if selspec != "error"
        ]

    def match(self, node: StyleNode) -> Style:
        results = sorted(
            (
                (specificity, order, declarations)
                for pred, specificity, order, declarations in self.selectors
                if pred(node)
            ),
            key=MATCH_SORT_KEY,
        )
        return merge_styles(*(decl for _, _, decl in results))  # type: ignore[arg-type]


MATCH_SORT_KEY = operator.itemgetter(0, 1)
