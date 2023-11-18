from functools import singledispatch


@singledispatch
def diagram_label(diagram):
    return diagram.name


@singledispatch
def paint_diagram_type(diagram) -> bool:
    return bool(diagram.diagramType)
