from functools import singledispatch


@singledispatch
def diagram_label(diagram):
    return diagram.name
