import sys

import pytest

from gaphor.plugins.errorreports.errorreports import ErrorReports


class ApplicationStub:
    pass


class ToolsMenuStub:
    def add_actions(self, provider):
        pass


@pytest.fixture
def error_reporter(event_manager):
    svc = ErrorReports(event_manager, ApplicationStub(), ToolsMenuStub())
    yield svc
    svc.shutdown()


def test_exception_stored(error_reporter):
    error_reporter.excepthook(*sys.exc_info())

    assert error_reporter.exceptions
