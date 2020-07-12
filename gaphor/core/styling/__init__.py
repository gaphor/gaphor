from __future__ import annotations

import operator
from typing import (
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import tinycss2
from typing_extensions import Literal, Protocol

from gaphor.core.styling.declarations import parse_declarations
from gaphor.core.styling.parser import SelectorError
from gaphor.core.styling.properties import (
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

    def parent(self) -> Optional[StyleNode]:
        ...

    def children(self) -> Iterator[StyleNode]:
        ...

    def attribute(self, name: str) -> str:
        ...

    def state(self) -> Sequence[str]:
        ...


def merge_styles(styles) -> Style:
    style: Style = {}
    for s in styles:
        style.update(s)
    return style


class CompiledStyleSheet:
    def __init__(self, css: str):
        self.selectors = [
            (selspec[0], selspec[1], order, declarations)
            for order, (selspec, declarations) in enumerate(parse_style_sheet(css))
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
        return merge_styles(decl for _, _, decl in results)


def parse_style_sheet(
    css,
) -> Generator[
    Union[
        Tuple[Tuple[Callable[[object], bool], Tuple[int, int, int]], Dict[str, object]],
        Tuple[Literal["error"], Union[tinycss2.ast.ParseError, SelectorError]],
    ],
    None,
    None,
]:
    rules = tinycss2.parse_stylesheet(
        css or "", skip_comments=True, skip_whitespace=True
    )
    for rule in rules:
        if rule.type == "error":
            yield ("error", rule)  # type: ignore[misc]
            continue

        if rule.type != "qualified-rule":
            continue

        try:
            selectors = compile_selector_list(rule.prelude)
        except SelectorError as e:
            yield ("error", e)  # type: ignore[misc]
            continue

        declaration = {
            prop: value
            for prop, value in parse_declarations(rule.content)
            if prop != "error" and value is not None
        }

        yield from ((selector, declaration) for selector in selectors)


MATCH_SORT_KEY = operator.itemgetter(0, 1)
