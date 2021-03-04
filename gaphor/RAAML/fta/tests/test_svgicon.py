from gaphor.RAAML.fta.svgicon import draw_svg_icon, load_svg_icon


def test_load_svg_icon():
    surface, width, height = load_svg_icon("and.svg")

    assert width > 0
    assert height > 0


def test_draw_svg_icon():
    surface, width, height = load_svg_icon("and.svg")

    draw_function = draw_svg_icon(surface)

    assert draw_function
