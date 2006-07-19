
import gobject
import gaphas
from gaphor import UML
from gaphor import resource
from gaphor.undomanager import get_undo_manager


class PlacementTool(gaphas.tool.PlacementTool):

    def __init__(self, item_factory, action_id, handle_index=-1, **properties):
        """item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        gaphas.tool.PlacementTool.__init__(self, factory=item_factory,
                                           handle_tool=gaphas.tool.HandleTool(),
                                           handle_index=handle_index)
        self.action_id = action_id
        self.is_released = False

    def on_button_press(self, context, event):
        self.is_released = False
        view = resource('MainWindow').get_current_diagram_view()
        view.unselect_all()
        #print 'Gaphor: on_button_press event: %s' % self.__dict__
        get_undo_manager().begin_transaction()
        return gaphas.tool.PlacementTool.on_button_press(self, context, event)
            
    def on_button_release(self, context, event):
        self.is_released = True
        if resource('reset-tool-after-create', False):
            resource('MainWindow').get_action_pool().get_action('Pointer').active = True
        get_undo_manager().commit_transaction()
        #print 'Gaphor: do_button_release event: %s' % self.__dict__
        return gaphas.tool.PlacementTool.on_button_release(self, context, event)

# vim:sw=4:et
