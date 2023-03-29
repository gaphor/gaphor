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
     font-size: 14;
     line-width: 2;
     padding: 0;
    }

    *:drop {
     color: #1a5fb4;
     line-width: 3;
    }

    *:disabled {
     opacity: 0.5;
    }

    @media dark-mode {
     * {
      color: white;
     }

     *:drop {
      color: #62a0ea;
     }
    }

    dependency,
    interfacerealization {
        dash-style: 7 5;
    }

    dependency[on_folded_interface = true],
    interfacerealization[on_folded_interface = true] {
        dash-style: 0;
    }

    controlflow {
        dash-style: 9 3;
    }
    """
)

DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    diagram {
     /* line-style: sloppy 0.3; */
    }
    """
)


class StyleSheet(Element):
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._system_font_family = "sans"
        self.compile_style_sheet()

    styleSheet: attribute[str] = attribute("styleSheet", str, DEFAULT_STYLE_SHEET)
    naturalLanguage: attribute[str] = attribute("naturalLanguage", str)

    @property
    def system_font_family(self) -> str:
        return self._system_font_family

    @system_font_family.setter
    def system_font_family(self, font_family: str):
        self._system_font_family = font_family
        self.compile_style_sheet()

    def compile_style_sheet(self) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(
            SYSTEM_STYLE_SHEET,
            f"* {{ font-family: {self._system_font_family} }}",
            self.styleSheet,
        )

    def match(self, node: StyleNode) -> Style:
        return self._compiled_style_sheet.match(node)

    def postload(self):
        super().postload()
        self.compile_style_sheet()

    def handle(self, event):
        # Ensure compiled style sheet is always up-to-date:
        if (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.styleSheet
        ):
            self.compile_style_sheet()

        super().handle(event)
