from __future__ import annotations

from gaphor.core.modeling import Element
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode


class StyleSheet(Element):
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.compile_style_sheet()

    styleSheet: attribute[str] = attribute("styleSheet", str, "")

    def compile_style_sheet(self) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(self.styleSheet)

    def match(self, node: StyleNode) -> Style:
        return self._compiled_style_sheet.match(node)

    def postload(self):
        super().postload()
        self.compile_style_sheet()

    def handle(self, event):
        # Ensure compiled style sheet is always up to date:
        if (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.styleSheet
        ):
            self.compile_style_sheet()

        super().handle(event)
