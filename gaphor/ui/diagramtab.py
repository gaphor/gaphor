#!/usr/bin/env python
# vim: sw=4:et

import gtk
from diagramview import DiagramView
from abstractwindow import AbstractWindow
from gaphor.diagram.itemtool import ItemTool

import diagramactions
import gaphor.diagram.actions

class DiagramTab(object):
    
    def __init__(self, owning_window):
        self.diagram = None
        self.owning_window = owning_window

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def get_canvas(self):
        return self.diagram.canvas

    def set_diagram(self, diagram):
        if self.diagram:
            self.diagram.disconnect(self.__on_diagram_event)
            self.diagram.canvas.disconnect(self.__undo_id)
            #self.diagram.canvas.disconnect(self.__snap_to_grid_id)
        self.diagram = diagram
        if diagram:
            diagram.canvas.set_property ('allow_undo', 1)
            diagram.connect(('name', '__unlink__'), self.__on_diagram_event)
            self.__undo_id = diagram.canvas.connect('undo', self.__on_diagram_undo)
            # Set capabilities:
            self.__on_diagram_undo(diagram.canvas)

    def construct(self):
        title = self.diagram and self.diagram.name or '<None>'

        table = gtk.Table(2,2, gtk.FALSE)
        #table.set_row_spacings (4)
        #table.set_col_spacings (4)

        frame = gtk.Frame()
        frame.set_shadow_type (gtk.SHADOW_IN)
        table.attach (frame, 0, 1, 0, 1,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        view = DiagramView (diagram=self.diagram)
        view.set_scroll_region(0, 0, 600, 450)

        frame.add (view)
        
        sbar = gtk.VScrollbar(view.get_vadjustment())
        table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        sbar = gtk.HScrollbar(view.get_hadjustment())
        table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                      gtk.FILL)

        view.connect('notify::tool', self.__on_view_notify_tool)
        view.connect_after('event-after', self.__on_view_event_after)
        view.connect('focus_item', self.__on_view_focus_item)
        view.connect('select_item', self.__on_view_select_item)
        view.connect('unselect_item', self.__on_view_select_item)
        self.view = view

	item_tool = ItemTool(self.owning_window.get_action_pool())
	view.get_default_tool().set_item_tool(item_tool)

        table.show_all()

        self.owning_window.new_tab(self, table, title)

    def close(self):
        """Tab is destroyed. Do the same thing that would
        be done if File->Close was pressed.
        """
        # Set diagram to None, so all refrences to the diagram are destroyed.
        self.owning_window.remove_tab(self)
        self.set_diagram(None)
        # We need this to get the view deleted properly:
        del self.view.diagram
        del self.view
        del self.diagram

    def __on_view_event_after(self, view, event):
        # handle mouse button 3 (popup menu):
        if event.type == gtk.gdk.BUTTON_PRESS:
            # First push the undo stack...
            view.canvas.push_undo(None)

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            vitem = view.focus_item
            if vitem:
                item = vitem.item
                popup_menu = item.get_popup_menu()
                if popup_menu:
                    self.owning_window._construct_popup_menu(menu_def=popup_menu,
                                           event=event)
                    return True
        return False

    def __on_view_focus_item(self, view, focus_item):
        self.owning_window.execute_action('ItemFocus')

    def __on_view_select_item(self, view, select_item):
        self.owning_window.execute_action('ItemSelect')

    def __on_view_notify_tool(self, view, pspec):
        self.owning_window.execute_action('ToolChange')

    def __on_diagram_undo(self, canvas):
        self.owning_window.execute_action('EditUndoStack')

    def __on_diagram_event(self, element, pspec):
        if pspec == '__unlink__':
            self.close()
        elif pspec.name == 'name':
            print 'Trying to set name to', element.name
            self.owning_window.set_tab_label(self, element.name)
            #self.get_window().set_title(self.diagram.name or '<None>')

