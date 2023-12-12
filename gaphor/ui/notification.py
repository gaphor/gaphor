from gi.repository import Adw

from gaphor.core import event_handler
from gaphor.event import Notification


class InAppNotifier:
    def __init__(self, toast_overlay):
        self.toast_overlay = toast_overlay
        self.latest_message: str | None = None

    @event_handler(Notification)
    def handle(self, event: Notification):
        if event.message != self.latest_message:
            self.latest_message = event.message
            toast = Adw.Toast.new(event.message)
            toast.connect("dismissed", self._on_dismissed)
            self.toast_overlay.add_toast(toast)
            return toast
        return None

    def _on_dismissed(self, toast):
        self.latest_message = None
