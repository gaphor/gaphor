
# vim:sw=4:et
import gobject
import gtk
from gtk.gdk import CONTROL_MASK, SHIFT_MASK
from gtk.gdk import BUTTON_PRESS, _2BUTTON_PRESS, BUTTON_PRESS_MASK
import diacanvas
from nameditem import NamedItem
from association import AssociationEnd

SHIFT_CONTROL_MASK = CONTROL_MASK | SHIFT_MASK

class ItemTool(diacanvas.view.Tool):
    __gsignals__ = {
        'button_press_event': 'override',
        'button_release_event': 'override',
        'motion_notify_event': 'override'
    }

    def __init__(self, action_pool):
        """item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        self.__gobject_init__()
        self.grabbed_item = None
        self.action_pool = action_pool

    def execute_action(self, action_id):
        self.action_pool.execute(action_id)

    def do_button_press_event(self, view, event):
        view_item = view.get_item_at(event.x, event.y)
        if not view_item:
            return False
        
        item = view_item.item

        if not item.flags & diacanvas.INTERACTIVE:
            return False

        # Select the item. Doesn't matter which mouse button was pressed.
        if event.state & CONTROL_MASK and view_item.is_selected():
            view.unselect(view_item)
            #view.focus(None)
            item.request_update()
            return True
        else:
            if not event.state & SHIFT_CONTROL_MASK and \
               not view_item.is_selected():
                #view.unselect_all()
                self.execute_action('EditDeselectAll')
            view.focus(view_item)

        if event.type == BUTTON_PRESS:
            # If Button1 is pressed, we're going to move the item.
            if event.button == 1:
                view.canvas.undo_manager.begin_transaction()
                self.grabbed_item = view_item
                self.old_pos = (event.x, event.y)
                item.request_update()

        elif event.type == _2BUTTON_PRESS:
            #view.canvas.undo_manager.begin_transaction()
            if isinstance(item, NamedItem):
                self.execute_action('RenameItem')
            elif hasattr(item, 'is_editable') and item.is_editable():
                self.execute_action('EditItem')
        return True

    def do_button_release_event(self, view, event):
        view.canvas.undo_manager.commit_transaction()
        if self.grabbed_item:
            self.grabbed_item = None
            return True
        return False

    def do_motion_notify_event(self, view, event):
        if self.grabbed_item and event.state & BUTTON_PRESS_MASK:
            view.move(event.x - self.old_pos[0], event.y - self.old_pos[1])
            self.old_pos = (event.x, event.y)
            return True
        return False


gobject.type_register(ItemTool)

