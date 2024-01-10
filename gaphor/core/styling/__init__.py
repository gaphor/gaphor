from __future__ import annotations

import functools
from collections.abc import Hashable
from typing import Callable, Iterator, Protocol, Sequence, TypedDict, Union

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
    WhiteSpace,
    declarations,
    number,
)

# Style is using SVG properties where possible
# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute
# NB1. The Style can also contain variables (start with `--`),
#      however those are not part of the interface.
# NB2. The Style can also contain private (`-gaphor-*`) entries.

Style = TypedDict(
    "Style",
    {
        "background-color": Color,
        "border-radius": Number,
        "color": Color,
        "content": str,
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
        "white-space": WhiteSpace,
        # Opaque elements to support inheritance
        "-gaphor-style-node": object,
        "-gaphor-compiled-style-sheet": object,
    },
    total=False,
)

INHERITED_DECLARATIONS = (
    "color",
    "font-family",
    "font-size",
    "font-style",
    "font-weight",
    "line-width",  # a.k.a. stroke-width
    "text-align",
    "text-color",
    "white-space",
)


class StyleNode(Hashable, Protocol):
    pseudo: str | None
    dark_mode: bool | None

    def name(self) -> str:
        ...

    def parent(self) -> StyleNode | None:
        ...

    def children(self) -> Iterator[StyleNode]:
        ...

    def attribute(self, name: str) -> str | None:
        """Obtain a string representation of an attribute.

        If the attribute does not exist, ``None`` is returned.
        """

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

    resolved_style = resolve_variables(style, styles)

    if abs_font_size and resolved_style["font-size"] in FONT_SIZE_VALUES:
        resolved_style["font-size"] = (
            abs_font_size * FONT_SIZE_VALUES[resolved_style["font-size"]]  # type: ignore[index]
        )

    if "opacity" in resolved_style:
        opacity = resolved_style["opacity"]
        for color_prop in ("color", "background-color", "text-color"):
            color: Color | None = resolved_style.get(color_prop)  # type: ignore[assignment]
            if color and color[3] > 0.0:
                resolved_style[color_prop] = color[:3] + (color[3] * opacity,)  # type: ignore[literal-required]

    return resolved_style


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
    """A style sheet, ready to compute styles for any StyleNode.

    The computed styles are cached, to speed up subsequent lookups.
    """

    def __init__(
        self,
        *css: str,
        rules: list[tuple[Callable[[StyleNode], bool], Style]] | None = None,
    ):
        self.rules: list[tuple[Callable[[StyleNode], bool], Style]] = rules or [
            (selector, declarations)  # type: ignore[misc]
            for selector, declarations in compile_style_sheet(*css)
            if selector != "error"
        ]
        # Use this trick to bind a cache per instance, instead of globally.
        self.compute_style = functools.lru_cache(maxsize=1000)(
            self._compute_style_uncached
        )

    def copy(self) -> CompiledStyleSheet:
        return CompiledStyleSheet(rules=self.rules)

    def _compute_style_uncached(self, node: StyleNode) -> Style:
        parent = node.parent()
        parent_style = self.compute_style(parent) if parent else {}
        return merge_styles(
            {n: v for n, v in parent_style.items() if n in INHERITED_DECLARATIONS},  # type: ignore[arg-type]
            *(declarations for selector, declarations in self.rules if selector(node)),
            {"-gaphor-style-node": node, "-gaphor-compiled-style-sheet": self},
        )
