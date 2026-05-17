from gi.repository import Adw, GLib

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
            if event.action_name and event.action_label:
                toast.set_action_name(event.action_name)
                toast.set_button_label(event.action_label)
                if event.action_target:
                    toast.set_action_target_value(
                        GLib.Variant.new_string(event.action_target)
                    )
            self.toast_overlay.add_toast(toast)
            return toast
        return None

    def _on_dismissed(self, toast):
        self.latest_message = None
