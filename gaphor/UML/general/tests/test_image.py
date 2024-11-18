from pathlib import Path

import pytest
from gaphas.solver import VERY_STRONG, Solver, Variable

from gaphor import UML
from gaphor.UML.general.image import AspectRatioConstraint, ImageItem


def test_image_property_minimum_size(create):
    image = create(ImageItem, UML.Image)

    assert image.min_width == 10
    assert image.min_height == 10


def test_image_property_set_size(create):
    image = create(ImageItem, UML.Image)

    image.load_image_from_file(Path("data/logos/gaphor-24x24.png"))

    assert image.width == 24
    assert image.height == 24


@pytest.mark.parametrize(
    ["ratio", "set_index", "set_value", "expect_width", "expect_height"],
    [
        [1.0, 0, 50.0, 50.0, 50.0],
        [0.4, 0, 50.0, 50.0, 125.0],
        [1.5, 1, 50.0, 75.0, 50.0],
        [1.0, 4, 2.0, 200.0, 100.0],
        # This values look off, due to how the weakest variable is determined:
        [1.0, 2, 50.0, 100.0, 100.0],
        [0.4, 2, 50.0, 40.0, 100.0],
    ],
)
def test_aspect_ratio_change(ratio, set_index, set_value, expect_width, expect_height):
    x0, y0, x1, y1 = (Variable(value=v, strength=VERY_STRONG) for v in [0, 0, 100, 100])
    ratio = Variable(value=ratio, strength=VERY_STRONG)
    solver = Solver()
    vars = [x0, y0, x1, y1, ratio]
    constraint = AspectRatioConstraint(*vars)
    solver.add_constraint(constraint)

    vars[set_index].value = set_value
    solver.solve()

    assert x1 - x0 == pytest.approx(expect_width)
    assert y1 - y0 == pytest.approx(expect_height)
