from __future__ import annotations

from gaphor.diagram.presentation import ElementPresentation


def align_left(elements: set[ElementPresentation]):
    left_edge = _left_edge(elements)

    for item in elements:
        item.matrix.translate(left_edge - item.matrix[4], 0)


def align_right(elements: set[ElementPresentation]):
    right_edge = _right_edge(elements)

    for item in elements:
        item.matrix.translate(right_edge - (item.matrix[4] + item.width), 0)


def align_vertical_center(elements: set[ElementPresentation]):
    left_edge = _left_edge(elements)
    right_edge = _right_edge(elements)
    center_edge = left_edge + (right_edge - left_edge) / 2

    for item in elements:
        item.matrix.translate(center_edge - item.matrix[4] - item.width / 2, 0)


def align_top(elements: set[ElementPresentation]):
    top_edge = _top_edge(elements)

    for item in elements:
        item.matrix.translate(0, top_edge - item.matrix[5])


def align_bottom(elements: set[ElementPresentation]):
    bottom_edge = _bottom_edge(elements)

    for item in elements:
        item.matrix.translate(0, bottom_edge - (item.matrix[5] + item.height))


def align_horizontal_center(elements: set[ElementPresentation]):
    top_edge = _top_edge(elements)
    bottom_edge = _bottom_edge(elements)
    center_edge = top_edge + (bottom_edge - top_edge) / 2

    for item in elements:
        item.matrix.translate(0, center_edge - item.matrix[5] - item.height / 2)


def resize_max_width(elements: set[ElementPresentation]):
    max_width = _max_width(elements)

    for item in elements:
        item.width = max_width


def resize_max_height(elements: set[ElementPresentation]):
    max_height = _max_height(elements)

    for item in elements:
        item.height = max_height


def resize_max_size(elements: set[ElementPresentation]):
    max_width = _max_width(elements)
    max_height = _max_height(elements)

    for item in elements:
        item.width = max_width
        item.height = max_height


def _left_edge(elements: set[ElementPresentation]):
    return min(item.matrix[4] for item in elements)


def _right_edge(elements: set[ElementPresentation]):
    return max(item.matrix[4] + item.width for item in elements)


def _top_edge(elements: set[ElementPresentation]):
    return min(item.matrix[5] for item in elements)


def _bottom_edge(elements: set[ElementPresentation]):
    return max(item.matrix[5] + item.height for item in elements)


def _max_width(elements: set[ElementPresentation]):
    return max(item.width for item in elements)


def _max_height(elements: set[ElementPresentation]):
    return max(item.height for item in elements)
