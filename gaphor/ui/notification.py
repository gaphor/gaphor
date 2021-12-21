from gi.repository import GLib

from gaphor.core import event_handler
from gaphor.event import Notification

DELAY = 5_000


class InAppNotifier:
    def __init__(self, builder):
        self.revealer = builder.get_object("notification-revealer")
        self.message_label = builder.get_object("notification-message")
        self.auto_hide_id = 0
        close = builder.get_object("notification-close")
        close.connect("clicked", self.close_notification)

    @event_handler(Notification)
    def handle(self, event: Notification):
        if not self.revealer.get_reveal_child():
            self.message_label.set_text(event.message)
            self.revealer.set_reveal_child(True)
            self.auto_hide_id = GLib.timeout_add(DELAY, self.close_notification)

    def close_notification(self, *args):
        self.revealer.set_reveal_child(False)
        if self.auto_hide_id:
            GLib.source_remove(self.auto_hide_id)
            self.auto_hide_id = 0
