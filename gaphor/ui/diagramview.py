import logging
import sys

from gaphas.view import GtkView
from gi.repository import GObject, Gtk

log = logging.getLogger(__name__)


class DiagramView(GtkView):
    __gtype_name__ = "DiagramView"

    @GObject.Signal(name="cut-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _cut_clipboard(self):
        log.info("cut-clipboard")

    @GObject.Signal(name="copy-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _copy_clipboard(self):
        log.info("copy-clipboard")

    @GObject.Signal(name="paste-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _paste_clipboard(self):
        log.info("paste-clipboard")

    @GObject.Signal(name="paste-full-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _paste_full_clipboard(self):
        log.info("paste-full-clipboard")


def _new_signal_shortcut(shortcut, signal):
    return Gtk.Shortcut.new(
        trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
        action=Gtk.SignalAction.new(signal),
    )


_mod = "<Meta>" if sys.platform == "darwin" else "<Control>"

DiagramView.add_shortcut(_new_signal_shortcut(f"{_mod}x", "cut-clipboard"))
DiagramView.add_shortcut(_new_signal_shortcut(f"{_mod}c", "copy-clipboard"))
DiagramView.add_shortcut(_new_signal_shortcut(f"{_mod}v", "paste-clipboard"))
DiagramView.add_shortcut(
    _new_signal_shortcut(f"{_mod}<Shift>v", "paste-full-clipboard")
)
del _mod


def _trigger_signal(signal_name):
    def _trigger_action(self, _action_name, _param):
        self.emit(signal_name)

    return _trigger_action


DiagramView.install_action("clipboard.cut", None, _trigger_signal("cut-clipboard"))
DiagramView.install_action("clipboard.copy", None, _trigger_signal("copy-clipboard"))
DiagramView.install_action("clipboard.paste", None, _trigger_signal("paste-clipboard"))
DiagramView.install_action(
    "clipboard.paste-full", None, _trigger_signal("paste-full-clipboard")
)
