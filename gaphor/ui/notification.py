from gi.repository import GLib

from gaphor.core import event_handler
from gaphor.ui.event import Notification

DELAY = 5_000


class InAppNotifier:
    def __init__(self, builder):
        self.revealer = builder.get_object("notification-revealer")
        self.message_label = builder.get_object("notification-message")
        builder.connect_signals(
            {
                "close-notification": close_notification,
            }
        )

    @event_handler(Notification)
    def handle(self, event: Notification):
        if not self.revealer.get_reveal_child():
            self.message_label.set_text(event.message)
            self.revealer.set_reveal_child(True)
            self.revealer.auto_hide_id = GLib.timeout_add(
                DELAY, close_notification, self.revealer
            )


def close_notification(notification_revealer):
    notification_revealer.set_reveal_child(False)
    GLib.source_remove(notification_revealer.auto_hide_id)
    del notification_revealer.auto_hide_id
