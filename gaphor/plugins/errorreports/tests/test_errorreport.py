import sys

import pytest

from gaphor.plugins.errorreports.errorreports import ErrorReports


class ApplicationStub:
    @property
    def active_session(self):
        return None


@pytest.fixture
def error_reporter(event_manager):
    svc = ErrorReports(ApplicationStub(), event_manager)
    svc.open()
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


def get_text(buffer):
    return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)


def test_exception_stored(error_reporter):
    error_reporter.excepthook(*exc_info())

    assert error_reporter.exceptions


def test_format_exception(error_reporter):
    error_reporter.excepthook(*exc_info())

    text = get_text(error_reporter.buffer)

    assert 'raise ValueError("Hello")' in text


def test_format_exception_group(error_reporter):
    error_reporter.excepthook(*exc_group_info())

    text = get_text(error_reporter.buffer)

    assert 'ValueError("Internal Error")' in text
