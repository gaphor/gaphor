"""
This is a special tool used for editing text on certain objects.
"""

import gtk
from zope.interface import Interface
from gaphas.tool import Tool


class IEditable(Interface):

    def is_editable(self, x, y):
        """Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        """

    def get_text(self):
        """Get the text to be updated
        """

    def get_bounds(self):
        """Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.
        """

    def update_text(self, self):
        """Update with the new text.
        """

    def key_pressed(self, pos, key):
        """Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """


class TextEditTool(Tool):
    """Text edit tool. Allows for elements that can adapt to the 
    IEditable interface to be edited.
    """

    def __init__(self):
        pass

    def create_edit_window(self, view, x,y, text):
        """Create a popup window with some editable text.
        """
        print 'Double click'
        window = gtk.Window()
        window.set_property('decorated', False)
        window.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        #window.set_modal(True)
        window.set_parent_window(context.view.window)
        buffer = gtk.TextBuffer()
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        window.add(text_view)
        window.size_allocate(gtk.gdk.Rectangle(int(event.x), int(event.y), 50, 50))
        #window.move(int(event.x), int(event.y))
        cursor_pos = context.view.get_toplevel().get_screen().get_display().get_pointer()
        print 'cursor_pos', cursor_pos
        window.move(cursor_pos[1], cursor_pos[2])
        window.connect('focus-out-event', self._on_focus_out_event, buffer)
        text_view.connect('key-press-event', self._on_key_press_event, buffer)
        #text_view.set_size_request(50, 50)
        window.show()
        #text_view.grab_focus()
        #window.set_uposition(event.x, event.y)
        #window.focus
        return True

    def on_double_click(self, context, event):
        text = ''
        # get item at cursor
        self.create_edit_window(context.view, event.x, event.y, text)

    def _on_key_press_event(self, widget, event, buffer):
        if event.keyval == gtk.keysyms.Return:
            print 'Enter!'
            #widget.get_toplevel().destroy()
        elif event.keyval == gtk.keysyms.Escape:
            print 'Escape!'
            widget.get_toplevel().destroy()

    def _on_focus_out_event(self, widget, event, buffer):
        print 'focus out!', buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        widget.destroy()


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


# vim: sw=4:et:ai
