import pytest
from gi.repository import Adw

from gaphor.event import Notification
from gaphor.ui.notification import InAppNotifier


@pytest.fixture
def in_app_notifier():
    return InAppNotifier(Adw.ToastOverlay.new())


def test_notifier_can_handle_message(in_app_notifier):
    toast = in_app_notifier.handle(Notification("a message"))

    assert toast


def test_notifier_can_collapse_multiple_messages(in_app_notifier):
    toast1 = in_app_notifier.handle(Notification("a message"))
    toast2 = in_app_notifier.handle(Notification("a message"))

    assert toast1
    assert not toast2


def test_notifier_show_messages_when_previous_message_is_dismissed(in_app_notifier):
    toast1 = in_app_notifier.handle(Notification("a message"))
    toast1.dismiss()
    toast2 = in_app_notifier.handle(Notification("a message"))

    assert toast2
