from __future__ import annotations

import importlib.resources
import textwrap

from gaphor.core.modeling.base import Base, Id, RepositoryProtocol
from gaphor.core.modeling.event import AttributeUpdated, StyleSheetUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet

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
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(
        self, id: Id | None = None, model: RepositoryProtocol | None = None
    ) -> None:
        super().__init__(id, model)
        self._instant_style_declarations = ""
        self._system_font_family = "sans"
        self.compile_style_sheet()

    styleSheet: attribute[str] = attribute("styleSheet", str, DEFAULT_STYLE_SHEET)
    naturalLanguage: attribute[str] = attribute("naturalLanguage", str)

    @property
    def instant_style_declarations(self) -> str:
        return self._instant_style_declarations

    @instant_style_declarations.setter
    def instant_style_declarations(self, declarations: str) -> None:
        self._instant_style_declarations = declarations
        self.compile_style_sheet()
        super().handle(StyleSheetUpdated(self))

    @property
    def system_font_family(self) -> str:
        return self._system_font_family

    @system_font_family.setter
    def system_font_family(self, font_family: str) -> None:
        self._system_font_family = font_family
        self.compile_style_sheet()

    def compile_style_sheet(self) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(
            SYSTEM_STYLE_SHEET,
            f"diagram {{ font-family: {self._system_font_family} }}",
            self.styleSheet,
            self._instant_style_declarations,
        )

    def new_compiled_style_sheet(self) -> CompiledStyleSheet:
        return self._compiled_style_sheet.copy()

    def postload(self) -> None:
        super().postload()
        self.compile_style_sheet()

    def handle(self, event: object) -> None:
        # Ensure compiled style sheet is always up-to-date:
        if is_style_sheet_update := (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.styleSheet
        ):
            self.compile_style_sheet()

        super().handle(event)

        if is_style_sheet_update or (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.naturalLanguage
        ):
            super().handle(StyleSheetUpdated(self))
