import cairo
import pytest
from gaphas.geometry import Rectangle

from gaphor.core.modeling.diagram import FALLBACK_STYLE
from gaphor.core.styling import JustifyContent
from gaphor.diagram.shapes import (
    Box,
    DrawContext,
    IconBox,
    Orientation,
    Text,
    TextAlign,
    UpdateContext,
    VerticalAlign,
)


@pytest.fixture
def fixed_text_size(monkeypatch):
    size = (60, 15)

    def text_size(*args):
        return size

    monkeypatch.setattr("gaphor.diagram.text.Layout.size", text_size)
    return size


@pytest.fixture
def update_context():
    return UpdateContext(style=FALLBACK_STYLE)


@pytest.fixture
def draw_context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cr = cairo.Context(surface)
    return DrawContext(
        cairo=cr,
        style=FALLBACK_STYLE,
        selected=False,
        focused=False,
        hovered=False,
        dropzone=False,
    )


def test_box_size(update_context):
    box = Box()

    assert box.size(context=update_context) == (0, 0)


def test_draw_empty_box(draw_context):
    box = Box(draw=None)

    box.draw(context=draw_context, bounding_box=Rectangle())


def test_draw_box_with_custom_draw_function(draw_context):
    called = False

    def draw(box, context, bounding_box):
        nonlocal called
        called = True

    box = Box(draw=draw)

    box.draw(context=draw_context, bounding_box=Rectangle())

    assert called


def test_draw_last_box_with_all_remaining_space(update_context, draw_context):
    bounding_boxes = []

    def draw(_box, _context, bounding_box):
        bounding_boxes.append(bounding_box)

    box = Box(
        Box(style={"min-height": 80}, draw=draw),
        Box(draw=draw),
        style={"vertical-align": VerticalAlign.TOP},
    )

    box.size(context=update_context, bounding_box=Rectangle(0, 0, 100, 120))
    box.draw(context=draw_context, bounding_box=Rectangle(0, 0, 100, 120))

    assert bounding_boxes[0].height == 80
    assert bounding_boxes[1].height == 40


def test_draw_box_with_horzontal_content(update_context, draw_context):
    bounding_boxes = []

    def draw(_box, _context, bounding_box):
        bounding_boxes.append(bounding_box)

    box = Box(
        Box(style={"min-width": 40}, draw=draw),
        Box(style={"min-width": 80}, draw=draw),
        orientation=Orientation.HORIZONTAL,
    )

    box.size(context=update_context, bounding_box=Rectangle(0, 0, 120, 100))
    box.draw(context=draw_context, bounding_box=Rectangle(0, 0, 120, 100))

    assert bounding_boxes[0].width == 40
    assert bounding_boxes[0].height == 100
    assert bounding_boxes[1].width == 80
    assert bounding_boxes[1].height == 100


def test_draw_box_with_stretched_content(update_context, draw_context):
    bounding_boxes = []

    def draw(_box, _context, bounding_box):
        bounding_boxes.append(bounding_box)

    box = Box(
        Box(draw=draw),
        Box(draw=draw),
        style={"justify-content": JustifyContent.STRETCH},
    )

    box.size(context=update_context, bounding_box=Rectangle(0, 0, 100, 120))
    box.draw(context=draw_context, bounding_box=Rectangle(0, 0, 100, 120))

    assert bounding_boxes[0].height == 60
    assert bounding_boxes[1].height == 60


def test_draw_box_with_stretched_oversized_content(draw_context, update_context):
    bounding_boxes = []

    def draw(_box, _context, bounding_box):
        bounding_boxes.append(bounding_box)

    box = Box(
        Box(draw=draw),
        Box(style={"min-height": 80}, draw=draw),
        style={"justify-content": JustifyContent.STRETCH},
    )

    box.size(context=update_context, bounding_box=Rectangle(0, 0, 100, 120))
    box.draw(context=draw_context, bounding_box=Rectangle(0, 0, 100, 120))

    assert bounding_boxes[0].y == 0
    assert bounding_boxes[0].height == 40
    assert bounding_boxes[1].y == 40
    assert bounding_boxes[1].height == 80


def test_draw_icon_box(draw_context):
    box_drawn = None

    def box_draw(box, context, bounding_box):
        nonlocal box_drawn
        box_drawn = bounding_box

    shape = IconBox(Box(draw=box_draw), Text(text="some text"))

    bounding_box = Rectangle(11, 12, 13, 14)
    shape.draw(draw_context, bounding_box)

    assert box_drawn == bounding_box


def test_icon_box_child_placement_center_bottom(update_context):
    style = {"text-align": TextAlign.CENTER, "vertical-align": VerticalAlign.BOTTOM}

    text = Text(text="some text")
    shape = IconBox(
        Box(),
        text,
    )
    shape.size(update_context)

    w, h = shape.sizes[0]
    bounding_box = Rectangle(0, 0, 10, 20)

    x, y, _, _ = shape.child_pos(style, bounding_box)

    assert x == (bounding_box.width - w) / 2
    assert y == bounding_box.height


def test_icon_box_child_placement_right_middle(update_context):
    style = {"text-align": TextAlign.RIGHT, "vertical-align": VerticalAlign.MIDDLE}

    text = Text(text="some text")
    shape = IconBox(
        Box(),
        text,
    )
    shape.size(update_context)

    w, h = shape.sizes[0]
    bounding_box = Rectangle(0, 0, 10, 20)

    x, y, _, _ = shape.child_pos(style, bounding_box)

    assert x == bounding_box.width
    assert y == (bounding_box.height - h) / 2


def test_icon_box_child_placement_left_middle(update_context):
    style = {"text-align": TextAlign.LEFT, "vertical-align": VerticalAlign.MIDDLE}

    text = Text(text="some text")
    shape = IconBox(
        Box(),
        text,
    )
    shape.size(update_context)

    w, h = shape.sizes[0]
    bounding_box = Rectangle(0, 0, 10, 20)

    x, y, _, _ = shape.child_pos(style, bounding_box)

    assert x == -w
    assert y == (bounding_box.height - h) / 2


def test_icon_box_child_placement_center_top(update_context):
    style = {"text-align": TextAlign.CENTER, "vertical-align": VerticalAlign.TOP}

    text = Text(text="some text")
    shape = IconBox(
        Box(),
        text,
    )
    shape.size(update_context)

    w, h = shape.sizes[0]
    bounding_box = Rectangle(0, 0, 10, 20)

    x, y, _, _ = shape.child_pos(style, bounding_box)

    assert x == (bounding_box.width - w) / 2
    assert y == -h


def test_text_has_width(update_context, fixed_text_size):
    text = Text(lambda: "some text")

    w, _ = text.size(update_context)
    assert w == fixed_text_size[0]


def test_text_has_height(update_context, fixed_text_size):
    text = Text("some text")

    _, h = text.size(update_context)
    assert h == fixed_text_size[1]


def test_text_with_min_width(update_context):
    style = {"min-width": 100, "min-height": 0}
    text = Text("some text", style=style)

    w, _ = text.size(update_context)
    assert w == 100


def test_text_width_min_height(update_context):
    style = {"min-width": 0, "min-height": 40}
    text = Text("some text", style=style)

    _, h = text.size(update_context)
    assert h == 40


def test_text_with_after_pseudo_element():
    after_style = {"content": " text"}
    style = {"color": (0, 0, 1, 1), "::after": after_style}
    text = Text("some")

    assert text.text(style) == "some text"
