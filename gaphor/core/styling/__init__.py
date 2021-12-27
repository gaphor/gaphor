from __future__ import annotations

import operator
from typing import Callable, Dict, Iterator, Literal, Protocol, Sequence, Tuple, Union

import tinycss2

from gaphor.core.styling.declarations import (
    FONT_SIZE_VALUES,
    number,
    parse_declarations,
)
from gaphor.core.styling.parser import SelectorError
from gaphor.core.styling.properties import (
    Color,
    FontStyle,
    FontWeight,
    Style,
    TextAlign,
    TextDecoration,
    VerticalAlign,
)
from gaphor.core.styling.selectors import compile_selector_list


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


Rule = Union[
    Tuple[Tuple[Callable[[object], bool], Tuple[int, int, int]], Dict[str, object]],
    Tuple[Literal["error"], Union[tinycss2.ast.ParseError, SelectorError]],
]


def merge_styles(*styles: Style) -> Style:
    style = Style()
    abs_font_size = None
    for s in styles:
        font_size = s.get("font-size")
        if font_size and isinstance(font_size, number):
            abs_font_size = font_size
        style.update(s)

    if abs_font_size and style["font-size"] in FONT_SIZE_VALUES:
        style["font-size"] = abs_font_size * FONT_SIZE_VALUES[style["font-size"]]  # type: ignore[index]

    if "opacity" in style:
        opacity = style["opacity"]
        for color_prop in ("color", "background-color", "text-color"):
            color: Color | None = style.get(color_prop)  # type: ignore[assignment]
            if color and color[3] > 0.0:
                style[color_prop] = color[:3] + (color[3] * opacity,)  # type: ignore[misc]

    return style


class CompiledStyleSheet:
    def __init__(self, *css: str):
        self.selectors = [
            (selspec[0], selspec[1], order, declarations)
            for order, (selspec, declarations) in enumerate(parse_style_sheets(*css))
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


def parse_style_sheets(*css: str) -> Iterator[Rule]:
    for sheet in css:
        yield from parse_style_sheet(sheet)


def parse_style_sheet(css: str) -> Iterator[Rule]:
    rules = tinycss2.parse_stylesheet(
        css or "", skip_comments=True, skip_whitespace=True
    )
    for rule in rules:
        if rule.type == "error":
            yield "error", rule
            continue

        if rule.type != "qualified-rule":
            continue

        try:
            selectors = compile_selector_list(rule.prelude)
        except SelectorError as e:
            yield "error", e
            continue

        declaration = {
            prop: value
            for prop, value in parse_declarations(rule.content)
            if prop != "error" and value is not None
        }

        yield from ((selector, declaration) for selector in selectors)


MATCH_SORT_KEY = operator.itemgetter(0, 1)
