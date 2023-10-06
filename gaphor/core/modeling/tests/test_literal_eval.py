import pytest

from gaphor.core.modeling.presentation import literal_eval


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
