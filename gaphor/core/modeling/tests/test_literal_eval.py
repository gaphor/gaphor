import sys

import pytest

from gaphor.core.modeling.presentation import literal_eval


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="literal_eval only strips leading spaces in Python 3.10+",
)
@pytest.mark.parametrize(
    "text,expected",
    [
        ("12", 12),
        ("  12", 12),
        ("12  ", 12),
        ("12\n  ", 12),
        (
            """[
        1, 2,
        3
        ]
        """,
            [1, 2, 3],
        ),
        (
            """
        [
        1, 2,
        3
        ]
        """,
            [1, 2, 3],
        ),
    ],
)
def test_literal_eval(text, expected):
    assert literal_eval(text) == expected
