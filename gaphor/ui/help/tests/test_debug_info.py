import sys

import pytest

from gaphor.ui.help import HelpService


class ApplicationStub:
    @property
    def active_session(self):
        return None

    @property
    def active_window(self):
        return None


@pytest.fixture
def help_service():
    svc = HelpService(ApplicationStub())
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


def test_exception_stored(help_service):
    help_service.excepthook(*exc_info())

    assert help_service.exceptions


def test_format_exception(help_service):
    help_service.excepthook(*exc_info())
    about_dialog = help_service.about()
    text = about_dialog.get_debug_info()

    assert 'raise ValueError("Hello")' in text


def test_format_exception_group(help_service):
    help_service.excepthook(*exc_group_info())
    about_dialog = help_service.about()
    text = about_dialog.get_debug_info()

    assert 'ValueError("Internal Error")' in text
