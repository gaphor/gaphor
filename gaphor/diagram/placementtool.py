
# vim:sw=4:et
import gobject
import diacanvas
from gaphor import UML
from gaphor import resource

class PlacementTool(diacanvas.PlacementTool):

    def __init__(self, item_factory, action_id, **properties):
        """item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        diacanvas.PlacementTool.__init__(self, None, **properties)
        self.item_factory = item_factory
        self.action_id = action_id
        self.is_released = False

    def _create_item(self, view, event):
        if event.button == 3:
            return None

        item = None

        try:
            item = self.item_factory()
        except Exception, e:
            log.error('Error while creating item: %s' % e, e)
        else:
            if self.properties and len(self.properties) > 0:
                try:
                    for (k, v) in self.properties.items():
                        item.set_property(k, v)
                except TypeError, e:
                    log.error('PlacementTool: could not set property %s' % k, e)

            item_at_mouse = view.get_item_at(event.x, event.y)
            log.debug('item at (%f %f)= %s' % (event.x, event.y, item_at_mouse))
            if item_at_mouse and item_at_mouse.item and hasattr(item_at_mouse.item, 'can_contain'):
                if item.get_property('parent'):
                    item.set_property('parent', None)
                log.debug('adding')
                item_at_mouse.item.add(item)
        return item

    def _move_item(self, view, event, item):
        """Move the newly created item to the desired position.
        """
        #wx, wy = view.window_to_world(event.x, event.y)
        ix, iy = item.affine_point_w2i(event.x, event.y)
        item.move(ix, iy)

    def _grab_handle(self, view, event, item):
        if not self.is_released:
            if isinstance(item, diacanvas.CanvasElement):
                self.handle_tool = diacanvas.view.HandleTool()
                #print 'PlacementTool: setting handle of Element'
                handle = item.handles[-1] #[diacanvas.HANDLE_SE]
                if handle.get_property('movable'):
                   self.handle_tool.set_grabbed_handle(handle)
                else:                
                    view_item = view.find_view_item(item)
                    view.focus(view_item)
                    if resource('reset-tool-after-create', False):
                        view.set_tool(None)
                    return
            else:
                diacanvas.PlacementTool._grab_handle(self, view, event, item)

    def do_button_press_event(self, view, event):
        self.is_released = False
        view.unselect_all()
        #print 'Gaphor: on_button_press_event: %s' % self.__dict__
        view.canvas.get_undo_manager().begin_transaction()
        return diacanvas.PlacementTool.do_button_press_event(self, view, event)

    def do_button_release_event(self, view, event):
        self.is_released = True
        if resource('reset-tool-after-create', False):
            view.set_tool(None)
        view.canvas.get_undo_manager().commit_transaction()
        #print 'Gaphor: do_button_release_event: %s' % self.__dict__
        return diacanvas.PlacementTool.do_button_release_event(self, view, event)

gobject.type_register(PlacementTool)

