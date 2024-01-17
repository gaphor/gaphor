import pytest

from gaphor.tests.raises import raises_exception_group


def test_capture_expected_exception():
    with raises_exception_group(ValueError):
        raise ExceptionGroup("msg", [ValueError()])


def test_capture_expected_from_multiple_exceptions():
    with raises_exception_group(ValueError):
        raise ExceptionGroup("msg", [TypeError(), ValueError()])


def test_propagate_unexpected_exception():
    with pytest.raises(ExceptionGroup):
        with raises_exception_group(ValueError):
            raise ExceptionGroup("msg", [TypeError()])


def test_propagate_wrong_exception():
    with pytest.raises(ValueError):
        with raises_exception_group(ValueError):
            raise ValueError()
