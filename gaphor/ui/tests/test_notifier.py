import pytest

from gaphor.ui.event import Notification
from gaphor.ui.mainwindow import new_builder
from gaphor.ui.notification import InAppNotifier


@pytest.fixture
def builder():
    return new_builder()


@pytest.fixture
def in_app_notifier(builder):
    return InAppNotifier(builder)


def test_notifier_has_widgets(in_app_notifier):
    assert in_app_notifier.revealer
    assert in_app_notifier.message_label


def test_notifier_can_handle_message(in_app_notifier):
    in_app_notifier.handle(Notification("a message"))

    assert in_app_notifier.revealer.get_reveal_child()
