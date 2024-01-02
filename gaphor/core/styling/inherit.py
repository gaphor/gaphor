from typing import Iterator, Sequence

from gaphor.core.styling import Style, StyleNode, merge_styles

INHERITED_DECLARATIONS = (
    "color",
    "font-family",
    "font-size",
    "font-style",
    "font-weight",
    "text-align",
    "text-color",
    "white-space",
)


class InheritingStyleNode:
    def __init__(self, parent: StyleNode, child: StyleNode):
        self._parent = parent
        self._child = child
        self.pseudo = parent.pseudo
        self.dark_mode = parent.dark_mode

    def name(self) -> str:
        return self._child.name()

    def parent(self) -> StyleNode | None:
        return self._parent

    def children(self) -> Iterator[StyleNode]:
        return self._child.children()

    def attribute(self, name: str) -> str:
        return self._child.attribute(name)

    def state(self) -> Sequence[str]:
        return self._parent.state()

    def __hash__(self):
        return hash((self._parent, self._child))

    def __eq__(self, other):
        return (
            isinstance(other, InheritingStyleNode)
            and self._parent == other._parent
            and self._child == other._child
        )


def inherit_style(style: Style, child: StyleNode) -> Style:
    parent: StyleNode | None = style.get(  # type: ignore[assignment]
        "-gaphor-style-node"
    )
    if not parent:
        return style

    node = InheritingStyleNode(parent, child)
    compiled_style_sheet = style.get("-gaphor-compiled-style-sheet")

    sub_style = compiled_style_sheet.match(node)  # type: ignore[attr-defined]

    return merge_styles(
        {n: v for n, v in style.items() if n in INHERITED_DECLARATIONS},  # type: ignore[arg-type]
        {"padding": (0, 0, 0, 0)},
        sub_style,
    )
