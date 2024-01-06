from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode


def compute_inherited_style(style: Style, style_node: StyleNode) -> Style:
    compiled_style_sheet: CompiledStyleSheet | None = style.get(
        "-gaphor-compiled-style-sheet"
    )  # type: ignore[assignment]

    return (
        compiled_style_sheet.compute_style(style_node)
        if compiled_style_sheet
        else style
    )
