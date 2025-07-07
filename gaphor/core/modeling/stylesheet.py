from __future__ import annotations

import importlib.resources
import textwrap

from gaphor.core.modeling.base import Base, Id, RepositoryProtocol
from gaphor.core.modeling.event import AttributeUpdated, StyleSheetUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, PrefersColorScheme, Style, StyleNode

SYSTEM_STYLE_SHEET = (importlib.resources.files("gaphor") / "diagram.css").read_text(
    "utf-8"
)

DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    diagram {
     /* line-style: sloppy 0.3; */
    }
    """
)


class StyleSheet(Base):
    def __init__(
        self, id: Id | None = None, model: RepositoryProtocol | None = None
    ) -> None:
        super().__init__(id, model)
        self._instant_style_declarations = ""
        self._system_font_family = "sans"
        self._compiled_cache: dict[PrefersColorScheme, CompiledStyleSheet] = {}

    styleSheet: attribute[str] = attribute("styleSheet", str, DEFAULT_STYLE_SHEET)
    naturalLanguage: attribute[str] = attribute("naturalLanguage", str)

    @property
    def instant_style_declarations(self) -> str:
        return self._instant_style_declarations

    @instant_style_declarations.setter
    def instant_style_declarations(self, declarations: str) -> None:
        self._instant_style_declarations = declarations
        self._style_sheet_updated()

    @property
    def system_font_family(self) -> str:
        return self._system_font_family

    @system_font_family.setter
    def system_font_family(self, font_family: str) -> None:
        self._system_font_family = font_family
        self._style_sheet_updated()

    def compute_style(
        self, node: StyleNode, prefers_color_scheme=PrefersColorScheme.NONE
    ) -> Style:
        return self.compile_style_sheet(prefers_color_scheme).compute_style(node)

    def compile_style_sheet(
        self, prefers_color_scheme=PrefersColorScheme.NONE
    ) -> CompiledStyleSheet:
        """Provide a compiled style sheet.

        Style sheets are cached, to speed up subsequent calls.
        """
        if compiled_style_sheet := self._compiled_cache.get(prefers_color_scheme):
            return compiled_style_sheet

        compiled_style_sheet = CompiledStyleSheet(
            SYSTEM_STYLE_SHEET,
            f"diagram {{ font-family: {self._system_font_family} }}",
            self.styleSheet,
            self._instant_style_declarations,
            prefers_color_scheme=prefers_color_scheme,
        )
        self._compiled_cache[prefers_color_scheme] = compiled_style_sheet
        return compiled_style_sheet

    def clear_caches(self):
        for compiled in self._compiled_cache.values():
            compiled.compute_style.cache_clear()

    def _style_sheet_updated(self):
        self._compiled_cache.clear()
        super().handle(StyleSheetUpdated(self))

    def handle(self, event: object) -> None:
        super().handle(event)

        if isinstance(event, AttributeUpdated) and event.property in (
            StyleSheet.styleSheet,
            StyleSheet.naturalLanguage,
        ):
            self._style_sheet_updated()
