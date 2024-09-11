from gi.repository import GLib

from gaphor.core.modeling import ModelReady
from gaphor.ui.modelchanged import ModelChanged
from gaphor.ui.tests.fixtures import iterate_until


def iteration(sentinel):
    ctx = GLib.main_context_default()
    while ctx.pending() and not sentinel:
        ctx.iteration(False)


def test_create_ui(event_manager):
    model_changed = ModelChanged(event_manager)

    widget = model_changed.open()

    assert widget


def test_monitor_file_changed(event_manager, tmp_path):
    new_file = tmp_path / "new_file"
    new_file.write_text("a", encoding="utf-8")

    model_changed = ModelChanged(event_manager)
    widget = model_changed.open()
    event_manager.handle(ModelReady(None, filename=new_file))

    new_file.write_text("b", encoding="utf-8")
    iterate_until(widget.get_revealed)

    assert widget.get_revealed()


def test_monitor_file_not_changed(event_manager, tmp_path):
    new_file = tmp_path / "new_file"
    new_file.write_text("a", encoding="utf-8")

    model_changed = ModelChanged(event_manager)
    widget = model_changed.open()
    event_manager.handle(ModelReady(None, filename=new_file))

    new_file.write_text("a", encoding="utf-8")
    iterate_until(condition=lambda: False, timeout=2)

    assert not widget.get_revealed()
