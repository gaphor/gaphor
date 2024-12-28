import logging

from gaphas.model import Model
from gaphas.view import GtkView
from gi.repository import GObject

from gaphor.diagram.selection import Selection
from gaphor.ui.actiongroup import named_shortcut

log = logging.getLogger(__name__)


class DiagramView(GtkView):
    __gtype_name__ = "DiagramView"

    def __init__(self, model: Model | None = None):
        super().__init__(model, Selection())

    @GObject.Signal(name="cut-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _cut_clipboard(self):
        pass

    @GObject.Signal(name="copy-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _copy_clipboard(self):
        pass

    @GObject.Signal(name="paste-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _paste_clipboard(self):
        pass

    @GObject.Signal(name="paste-full-clipboard", flags=GObject.SignalFlags.RUN_LAST)
    def _paste_full_clipboard(self):
        pass

    @GObject.Signal(name="delete", flags=GObject.SignalFlags.RUN_LAST)
    def _delete(self):
        pass


def _trigger_signal(signal_name):
    def _trigger_action(self, _action_name, _param):
        self.emit(signal_name)

    return _trigger_action


if hasattr(DiagramView, "install_action"):
    # Deal with Gtk being mocked when generating docs
    DiagramView.install_action("clipboard.cut", None, _trigger_signal("cut-clipboard"))
    DiagramView.install_action(
        "clipboard.copy", None, _trigger_signal("copy-clipboard")
    )
    DiagramView.install_action(
        "clipboard.paste", None, _trigger_signal("paste-clipboard")
    )
    DiagramView.install_action(
        "clipboard.paste-full", None, _trigger_signal("paste-full-clipboard")
    )
    DiagramView.install_action("diagram.delete", None, _trigger_signal("delete"))

    DiagramView.add_shortcut(named_shortcut("<Primary>x", "clipboard.cut"))
    DiagramView.add_shortcut(named_shortcut("<Primary>c", "clipboard.copy"))
    DiagramView.add_shortcut(named_shortcut("<Primary>v", "clipboard.paste"))
    DiagramView.add_shortcut(
        named_shortcut("<Primary><Shift>v", "clipboard.paste-full")
    )
    DiagramView.add_shortcut(
        named_shortcut("Delete|BackSpace|<Meta>BackSpace", "diagram.delete")
    )
