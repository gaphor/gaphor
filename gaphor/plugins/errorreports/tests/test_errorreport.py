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
    yield svc
    svc.shutdown()


def test_exception_stored(error_reporter):
    error_reporter.excepthook(*sys.exc_info())

    assert error_reporter.exceptions
