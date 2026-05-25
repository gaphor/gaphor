from gi.repository import Gtk

from gaphor.diagram.event import ToolCompleted


def reset_tool(event_manager):
    click = Gtk.GestureClick.new()
    click.set_button(3)
    click.connect("released", on_released, event_manager)
    return click


def on_released(gesture, n_press: int, _x: float, _y: float, event_manager) -> None:
    event_manager.handle(ToolCompleted(cancelled=True))
