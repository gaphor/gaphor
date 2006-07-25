
import gobject
import gtk
import gaphas
from gaphas.tool import Tool
from gaphor import UML
from gaphor import resource
from gaphor.undomanager import get_undo_manager

from interfaces import IEditor


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
        view = context.view #resource('MainWindow').get_current_diagram_view()
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


class TextEditTool(Tool):
    """Text edit tool. Allows for elements that can adapt to the 
    IEditable interface to be edited.
    """

    def __init__(self):
        pass

    def create_edit_window(self, view, x,y, text, *args):
        """Create a popup window with some editable text.
        """
        print 'Double click'
        window = gtk.Window()
        window.set_property('decorated', False)
        window.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        #window.set_modal(True)
        window.set_parent_window(view.window)
        buffer = gtk.TextBuffer()
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        window.add(text_view)
        window.size_allocate(gtk.gdk.Rectangle(int(x), int(y), 50, 50))
        #window.move(int(x), int(y))
        cursor_pos = view.get_toplevel().get_screen().get_display().get_pointer()
        print 'cursor_pos', cursor_pos
        window.move(cursor_pos[1], cursor_pos[2])
        window.connect('focus-out-event', self._on_focus_out_event, buffer, *args)
        text_view.connect('key-press-event', self._on_key_press_event, buffer, *args)
        #text_view.set_size_request(50, 50)
        window.show()
        #text_view.grab_focus()
        #window.set_uposition(event.x, event.y)
        #window.focus

    def on_double_click(self, context, event):
        view = context.view
        item = view.hovered_item
        if item:
            try:
                editor = IEditor(item)
            except TypeError:
                # Could not adapt to IEditor
                return False
            x, y = view.transform_point_c2i(item, event.x, event.y)
            if editor.is_editable(x, y):
                text = editor.get_text()
                # get item at cursor
                self.create_edit_window(context.view, event.x, event.y, text, editor)
                return True

    def _on_key_press_event(self, widget, event, buffer, editor):
        
        if event.keyval == gtk.keysyms.Return:
            print 'Enter!'
            #widget.get_toplevel().destroy()
        elif event.keyval == gtk.keysyms.Escape:
            print 'Escape!'
            widget.get_toplevel().destroy()

    def _on_focus_out_event(self, widget, event, buffer, editor):
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        print 'focus out!', text
        editor.update_text(text)
        widget.destroy()


from gaphas.tool import ToolChain, HoverTool, HandleTool, ItemTool, RubberbandTool

def DefaultTool():
    """The default tool chain build from HoverTool, ItemTool and HandleTool.
    """
    chain = ToolChain()
    chain.append(HoverTool())
    chain.append(HandleTool())
    chain.append(ItemTool())
    chain.append(TextEditTool())
    chain.append(RubberbandTool())
    return chain


# vim:sw=4:et:ai
