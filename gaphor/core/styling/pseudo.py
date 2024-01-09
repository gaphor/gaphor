from typing import Iterator, Sequence

from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode


class PseudoStyleNode:
    def __init__(self, node: StyleNode, psuedo: str | None):
        self._node = node
        self.pseudo = psuedo
        self.dark_mode = node.dark_mode

    def name(self) -> str:
        return self._node.name()

    def parent(self) -> StyleNode | None:
        return self._node.parent()

    def children(self) -> Iterator[StyleNode]:
        return self._node.children()

    def attribute(self, name: str) -> str | None:
        return self._node.attribute(name)

    def state(self) -> Sequence[str]:
        return self._node.state()

    def __hash__(self):
        return hash((self._node, self.pseudo))

    def __eq__(self, other):
        return (
            isinstance(other, PseudoStyleNode)
            and self._node == other._node
            and self.pseudo is other.pseudo
        )


def compute_pseudo_element_style(style: Style, pseudo: str) -> Style:
    parent: StyleNode | None = style.get("-gaphor-style-node")  # type: ignore[assignment]
    if not parent:
        return style

    compiled_style_sheet: CompiledStyleSheet = style.get("-gaphor-compiled-style-sheet")  # type: ignore[assignment]

    return compiled_style_sheet.compute_style(PseudoStyleNode(parent, pseudo))
