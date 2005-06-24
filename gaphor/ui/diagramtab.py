#!/usr/bin/env python
# vim: sw=4:et

import gtk

from gaphor import UML
from gaphor import resource
from gaphor.diagram.itemtool import ItemTool
from gaphor.diagram import get_diagram_item
from gaphor.undomanager import get_undo_manager
from gaphor.ui.diagramview import DiagramView
from gaphor.ui.abstractwindow import AbstractWindow

import gaphor.ui.diagramactions
import gaphor.diagram.placementactions

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
            #self.diagram.canvas.disconnect(self.__undo_id)
            #self.diagram.canvas.disconnect(self.__snap_to_grid_id)
        self.diagram = diagram
        if diagram:
            #log.info('set diagram')
            diagram.canvas.set_property ('allow_undo', 1)
            diagram.connect(('name', '__unlink__'), self.__on_diagram_event)
            #self.__undo_id = diagram.canvas.undo_manager.connect('begin_transaction', self.__on_diagram_undo)
            # Set capabilities:
            #self.__on_diagram_undo(diagram.canvas.undo_manager)

    def construct(self):
        title = self.diagram and self.diagram.name or '<None>'

        table = gtk.Table(2,2, False)
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
        view.connect('focus-item', self.__on_view_focus_item)
        view.connect('select-item', self.__on_view_select_item)
        view.connect('unselect-item', self.__on_view_select_item)
        view.connect_after('key-press-event', self.__on_key_press_event)
        view.connect('drag_data_received', self.__on_drag_data_received)
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
        #del self.view.diagram
        del self.view
        del self.diagram

    def __on_key_press_event(self, view, event):
        """Handle the 'Delete' key. This can not be handled directly (through
        GTK's accelerators) since otherwise this key will confuse the text
        edit stuff.
        """
        if view.is_focus():
            if event.keyval == 0xFFFF and event.state == 0: # Delete
                self.owning_window.execute_action('EditDelete')


    def __on_view_event_after(self, view, event):
        # handle mouse button 3 (popup menu):
        if event.type == gtk.gdk.BUTTON_PRESS:
            # First push the undo stack...
            #view.canvas.push_undo(None)
            pass
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

#    def __on_diagram_undo(self, undo_manager):
#        #log.info('set undo stack %s' % (undo_manager))
#        self.owning_window.execute_action('editundostack')

    def __on_diagram_event(self, element, pspec):
        if pspec == '__unlink__':
            self.close()
        elif pspec.name == 'name':
            print 'Trying to set name to', element.name
            self.owning_window.set_tab_label(self, element.name)
            #self.get_window().set_title(self.diagram.name or '<None>')

    def __on_drag_data_received(self, view, context, x, y, data, info, time):
        #print 'drag_data_received'
        if data and data.format == 8 and info == DiagramView.TARGET_ELEMENT_ID:
            #print 'drag_data_received:', data.data, info
            elemfact = resource(UML.ElementFactory)
            element = elemfact.lookup(data.data)
            assert element

            # TODO: use adapters to execute code below

            item_class = get_diagram_item(type(element))
            if isinstance(element, UML.Diagram):
                self.owning_window.execute_action('OpenModelElement')
            elif item_class:
                get_undo_manager().begin_transaction()
                item = self.diagram.create(item_class)
                assert item
                wx, wy = view.window_to_world(x + view.get_hadjustment().value,
                                              y + view.get_vadjustment().value)

                ix, iy = item.affine_point_w2i(max(0, wx), max(0, wy))
                item.move(ix, iy)
                item.set_property ('subject', element)
                get_undo_manager().commit_transaction()
                view.unselect_all()
                view.focus(view.find_view_item(item))

                self.owning_window.execute_action('ItemDiagramDrop')

            else:
                log.warning ('No graphical representation for UML element %s' % type(element).__name__)
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

