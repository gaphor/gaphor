from gi.repository import GLib

from gaphor.event import ModelChangedOnDisk
from gaphor.ui.modelchanged import ModelChanged


def iteration():
    ctx = GLib.main_context_default()
    while ctx.pending():
        ctx.iteration(False)


def test_create_ui(event_manager):
    model_changed = ModelChanged(event_manager)

    widget = model_changed.open()

    assert widget


def test_monitor_file_changed(event_manager, tmp_path):
    new_file = tmp_path / "new_file"
    new_file.write_text("a")

    model_changed = ModelChanged(event_manager)
    widget = model_changed.open()
    event_manager.handle(ModelChangedOnDisk(model_changed, new_file))

    new_file.write_text("b")
    iteration()

    assert widget.get_revealed()
