from __future__ import annotations

import textwrap

from gaphor.core.modeling import Element
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode

DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    * {
     background-color: transparent;
     color: black;
     font-family: sans;
     font-size: 14;
     highlight-color: rgba(0, 0, 255, 0.4);
     line-width: 2;
     padding: 0;
    }

    diagram {
     background-color: white;
     line-style: normal;
     /* line-style: sloppy 0.3; */
    }
    """
)


class StyleSheet(Element):
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.compile_style_sheet()

    styleSheet: attribute[str] = attribute("styleSheet", str, DEFAULT_STYLE_SHEET)

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
