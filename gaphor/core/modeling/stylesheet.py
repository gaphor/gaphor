from __future__ import annotations

import textwrap

from gaphor.core.modeling.element import Element
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode

SYSTEM_STYLE_SHEET = textwrap.dedent(
    """\
    * {
     background-color: transparent;
     color: black;
     font-family: sans;
     font-size: 14;
     line-width: 2;
     padding: 0;
    }

    *:drop {
     color: hsl(210, 100%, 25%);
     line-width: 3;
    }

    *:disabled {
     opacity: 0.5;
    }

    diagram {
     background-color: transparent;
    }

    dependency,
    interfacerealization {
        dash-style: 7 5;
    }

    dependency[on_folded_interface = true],
    interfacerealization[on_folded_interface = true] {
        dash-style: 0;
    }
    """
)

DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    * {
     background-color: transparent;
     color: black;
     font-family: sans;
     font-size: 14;
    }

    diagram {
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
        self._compiled_style_sheet = CompiledStyleSheet(
            SYSTEM_STYLE_SHEET, self.styleSheet
        )

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
