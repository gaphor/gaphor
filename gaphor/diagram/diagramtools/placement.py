import logging
from typing import Callable, Optional, Type, TypeVar

from gaphas.aspect.handlemove import HandleMove
from gaphas.tool.itemtool import MoveType
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.event import DiagramItemPlaced
from gaphor.diagram.grouping import Group
from gaphor.diagram.presentation import Presentation

log = logging.getLogger(__name__)

P = TypeVar("P", bound=Presentation, covariant=True)
FactoryType = Callable[[Diagram, Optional[Presentation]], Presentation]
ConfigFuncType = Callable[[P], None]


class PlacementState:
    def __init__(
        self, factory: FactoryType, event_manager: EventManager, handle_index: int
    ):
        self.factory = factory
        self.event_manager = event_manager
        self.handle_index = handle_index
        self.moving: Optional[MoveType] = None


def placement_tool(
    view: GtkView, factory: FactoryType, event_manager, handle_index: int
):
    gesture = Gtk.GestureDrag.new(view)
    placement_state = PlacementState(factory, event_manager, handle_index)
    gesture.connect("drag-begin", on_drag_begin, placement_state)
    gesture.connect("drag-update", on_drag_update, placement_state)
    gesture.connect("drag-end", on_drag_end, placement_state)
    return gesture


def on_drag_begin(gesture, start_x, start_y, placement_state):
    view = gesture.get_widget()
    gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    item = create_item(view, placement_state.factory, start_x, start_y)

    handle = item.handles()[placement_state.handle_index]
    if handle.movable:
        connect_opposite_handle(
            view, item, start_x, start_y, placement_state.handle_index
        )
        placement_state.moving = HandleMove(item, handle, view)
        placement_state.moving.start_move((start_x, start_y))
    else:
        placement_state.event_manager.handle(DiagramItemPlaced(item))

    view.selection.dropzone_item = None


def create_item(view, factory, x, y):
    selection = view.selection
    parent = selection.dropzone_item
    item = factory(view.model, parent)
    x, y = view.get_matrix_v2i(item).transform_point(x, y)
    item.matrix.translate(x, y)
    selection.unselect_all()
    view.selection.focused_item = item
    return item


def connect_opposite_handle(view, new_item, x, y, handle_index):
    try:
        opposite = new_item.opposite(new_item.handles()[handle_index])
    except (KeyError, AttributeError):
        pass
    else:
        if opposite.connectable:
            vpos = (x, y)
            handle_move = HandleMove(new_item, opposite, view)
            sink = handle_move.glue(vpos)
            if sink:
                handle_move.connect(vpos)


def on_drag_update(gesture, offset_x, offset_y, placement_state):
    if placement_state.moving:
        _, x, y = gesture.get_start_point()
        placement_state.moving.move((x + offset_x, y + offset_y))


def on_drag_end(gesture, offset_x, offset_y, placement_state):
    if placement_state.moving:
        view = gesture.get_widget()
        _, x, y = gesture.get_start_point()
        item = placement_state.moving.item
        placement_state.moving.stop_move((x + offset_x, y + offset_y))
        connect_opposite_handle(view, item, x, y, placement_state.handle_index)
        placement_state.event_manager.handle(DiagramItemPlaced(item))


def new_item_factory(
    item_class: Type[Presentation],
    subject_class: Optional[Type[Element]] = None,
    config_func: Optional[ConfigFuncType] = None,
):
    """``config_func`` may be a function accepting the newly created item."""

    def item_factory(diagram, parent=None):
        if subject_class:
            element_factory = diagram.model
            subject = element_factory.create(subject_class)
        else:
            subject = None

        item = diagram.create(item_class, subject=subject)

        adapter = Group(parent, item)
        if parent and adapter.can_contain():
            item.parent = parent
            adapter.group()

        if config_func:
            config_func(item)

        return item

    item_factory.item_class = item_class  # type: ignore[attr-defined]
    return item_factory
