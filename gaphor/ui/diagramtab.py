#!/usr/bin/env python
# vim: sw=4:et

import gtk

from gaphor import UML
from gaphor.core import inject
from gaphor.i18n import _
from gaphor.diagram.interfaces import IPopupMenu
from gaphor.diagram import get_diagram_item
from gaphor.transaction import Transaction
from gaphor.ui.diagramview import DiagramView
from gaphor.ui.abstractwindow import AbstractWindow
from event import DiagramItemFocused
from zope import component

class DiagramTab(object):
    
    element_factory = inject('element_factory')

    def __init__(self, owning_window):
        self.diagram = None
        #self.view = None
        self.owning_window = owning_window

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def get_canvas(self):
        return self.diagram.canvas

    def set_diagram(self, diagram):
        if self.diagram:
            self.diagram.disconnect(self._on_diagram_event)
            #self.diagram.canvas.disconnect(self.__undo_id)
            #self.diagram.canvas.disconnect(self.__snap_to_grid_id)
        self.diagram = diagram
        if diagram:
            diagram.connect(('name', '__unlink__'), self._on_diagram_event)

            if hasattr(self, 'view'):
                self.view.hadjustment.set_value(0.0)
                self.view.vadjustment.set_value(0.0)


    def construct(self):
        title = self.diagram and self.diagram.name or _('<None>')

        table = gtk.Table(2,2, False)
        #table.set_row_spacings(4)
        #table.set_col_spacings(4)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        table.attach(frame, 0, 1, 0, 1,
                     gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                     gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        view = DiagramView(diagram=self.diagram)
        #view.set_scroll_region(0, 0, 600, 450)

        frame.add(view)
        
        sbar = gtk.VScrollbar(view.vadjustment)
        table.attach(sbar, 1, 2, 0, 1, gtk.FILL,
                     gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        sbar = gtk.HScrollbar(view.hadjustment)
        table.attach(sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                     gtk.FILL)

        #view.connect('notify::tool', self._on_view_notify_tool)
        view.connect('focus-changed', self._on_view_focus_changed)
        view.connect('selection-changed', self._on_view_selection_changed)
        #view.connect('unselect-item', self._on_view_selection_changed)
        view.connect_after('key-press-event', self._on_key_press_event)
        view.connect('drag-data-received', self._on_drag_data_received)

        #item_tool = ItemTool(self.owning_window.get_action_pool())
        #view.get_default_tool().set_item_tool(item_tool)
        self.view = view

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

    def _on_key_press_event(self, view, event):
        """
        Handle the 'Delete' key. This can not be handled directly (through
        GTK's accelerators) since otherwise this key will confuse the text
        edit stuff.
        """
        if view.is_focus():
            if event.keyval == 0xFFFF and event.state == 0: # Delete
                self.owning_window.execute_action('EditDelete')


    def _on_view_focus_changed(self, view, focus_item):
        self.owning_window.execute_action('ItemFocus')
        component.handle(DiagramItemFocused(focus_item))

    def _on_view_selection_changed(self, view, selection):
        self.owning_window.execute_action('ItemSelect')

    def _on_view_notify_tool(self, view, pspec):
        self.owning_window.execute_action('ToolChange')

    def _on_diagram_event(self, element, pspec):
        if pspec == '__unlink__':
            self.close()
        elif pspec.name == 'name':
            print 'Trying to set name to', element.name
            self.owning_window.set_tab_label(self, element.name)
            #self.get_window().set_title(self.diagram.name or '<None>')

    def _on_drag_data_received(self, view, context, x, y, data, info, time):
        """
        Handle data dropped on the canvas.
        """
        #print 'drag_data_received'
        if data and data.format == 8 and info == DiagramView.TARGET_ELEMENT_ID:
            #print 'drag_data_received:', data.data, info
            element = self.element_factory.lookup(data.data)
            assert element

            # TODO: use adapters to execute code below

            item_class = get_diagram_item(type(element))
            if isinstance(element, UML.Diagram):
                self.owning_window.execute_action('OpenModelElement')
            elif item_class:
                tx = Transaction()
                item = self.diagram.create(item_class)
                assert item
                wx, wy = view.transform_point_c2w(x + view.hadjustment.value,
                                              y + view.vadjustment.value)

                ix, iy = view.canvas.get_matrix_w2i(item, calculate=True).transform_point(max(0, wx), max(0, wy))
                item.matrix.translate(ix, iy)
                item.subject = element
                tx.commit()
                view.unselect_all()
                view.focused_item = item

                self.owning_window.execute_action('ItemDiagramDrop')

            else:
                log.warning('No graphical representation for UML element %s' % type(element).__name__)
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

