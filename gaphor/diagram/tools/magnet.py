"""Magnet tool pulls or pushes the right or bottom side depending on mouse
movement."""

from gaphas.canvas import ancestors
from gaphas.move import Move
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.diagram.event import ToolCompleted


def magnet_tool(view: GtkView, event_manager) -> Gtk.GestureDrag:
    """Handle item movement and movement of handles."""
    gesture = (
        Gtk.GestureDrag.new(view)
        if Gtk.get_major_version() == 3
        else Gtk.GestureDrag.new()
    )
    drag_state = DragState(event_manager)
    gesture.connect("drag-begin", on_drag_begin, drag_state)
    gesture.connect("drag-update", on_drag_update, drag_state)
    gesture.connect("drag-end", on_drag_end, drag_state)
    return gesture


class DragState:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.reset()

    def reset(self):
        self.direction = 0
        self.moving_items = set()


def on_drag_begin(gesture, start_x, start_y, drag_state):
    drag_state.reset()
    gesture.set_state(Gtk.EventSequenceState.CLAIMED)


def on_drag_update(gesture, offset_x, offset_y, drag_state):
    _, sx, sy = gesture.get_start_point()
    view = gesture.get_widget()

    if not drag_state.direction:
        if abs(offset_x) > 10 and abs(offset_x) > abs(offset_y):
            drag_state.direction = 1
            drag_state.moving_items = set(
                moving_items(
                    view,
                    set(view.get_items_in_rectangle((sx, -100000, 10000000, 1000000))),
                )
            )
            for moving in drag_state.moving_items:
                moving.start_move((sx, 0))
        elif abs(offset_y) > 10 and abs(offset_y) > abs(offset_x):
            drag_state.direction = 2
            drag_state.moving_items = set(
                moving_items(
                    view,
                    set(view.get_items_in_rectangle((-100000, sy, 10000000, 1000000))),
                )
            )
            for moving in drag_state.moving_items:
                moving.start_move((0, sy))
        else:
            return

    if drag_state.direction == 1:
        x = sx + offset_x
        y = 0
    elif drag_state.direction == 2:
        x = 0
        y = sy + offset_y

    for moving in drag_state.moving_items:
        moving.move((x, y))

    view.magnet = (drag_state.direction, x, y)
    view.update_back_buffer()


def moving_items(view, selected_items):
    for item in selected_items:
        # Do not move subitems of selected items
        if not set(ancestors(view.model, item)).intersection(selected_items):
            yield Move(item, view)


def on_drag_end(gesture, offset_x, offset_y, drag_state):
    view = gesture.get_widget()
    _, x, y = gesture.get_start_point()
    for moving in drag_state.moving_items:
        moving.stop_move((x + offset_x, y + offset_y))
    drag_state.reset()
    view.update_back_buffer()
    drag_state.event_manager.handle(ToolCompleted())
    try:
        del view.magnet
    except AttributeError:
        pass


class MagnetPainter:
    def __init__(self, view: GtkView):
        self.view = view

    def paint(self, _items, cr):
        try:
            magnet = self.view.magnet
        except AttributeError:
            return

        view = self.view
        allocation = view.get_allocation()
        w, h = allocation.width, allocation.height
        direction, x, y = magnet

        cr.save()
        try:
            cr.identity_matrix()
            cr.set_line_width(6)
            cr.set_source_rgba(0.0, 0.3, 0.3, 0.3)
            if direction == 1:
                cr.move_to(x, 0)
                cr.line_to(x, h)
            elif direction == 2:
                cr.move_to(0, y)
                cr.line_to(w, y)
            cr.stroke()
        finally:
            cr.restore()
