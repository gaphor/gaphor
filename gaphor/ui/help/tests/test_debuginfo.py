import sys

import pytest

from gaphor.ui.help.debuginfo import DebugInfo


class ApplicationStub:
    @property
    def active_session(self):
        return None


@pytest.fixture
def debug_info():
    svc = DebugInfo(ApplicationStub())
    yield svc
    svc.shutdown()


def exc_info():
    try:
        raise ValueError("Hello")
    except ValueError:
        return sys.exc_info()


def exc_group_info():
    def nested():
        raise ValueError("Internal Error")

    try:
        nested()
    except ValueError as e:
        exc = e
    try:
        raise ExceptionGroup("Group", [exc, exc])
    except ExceptionGroup:
        return sys.exc_info()


def test_exception_stored(debug_info):
    debug_info.excepthook(*exc_info())

    assert debug_info.exceptions


def test_format_exception(debug_info):
    debug_info.excepthook(*exc_info())
    text = debug_info.create_debug_info()

    assert 'raise ValueError("Hello")' in text


def test_format_exception_group(debug_info):
    debug_info.excepthook(*exc_group_info())
    text = debug_info.create_debug_info()

    assert 'ValueError("Internal Error")' in text
