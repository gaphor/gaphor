#!/usr/bin/env python
# vim: sw=4:et

import gtk
from diagramview import DiagramView
from abstractwindow import AbstractWindow

class DiagramWindow(AbstractWindow):
    
    toolbar = (
            #'InsertActor',
            #'InsertUseCase',
            'Pointer',
            'separator',
            'InsertClass',
            'InsertPackage',
            'separator',
            'InsertAssociation',
            'InsertDependency',
            'InsertGeneralization',
            'separator',
            'InsertComment',
            'InsertCommentLine')

    menu = ('_File', (
                'FileExportSVG',
                'separator',
                'FileClose'),
            '_Edit', (
                'EditUndo',
                'EditRedo',
                'separator',
                'EditDelete',
                'separator',
                'EditSelectAll',
                'EditDeselectAll'),
            '_View', (
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100',
                'separator',
                'SnapToGrid'),
            '_Insert', 
                toolbar
            )
                #'InsertActor',
#                #'InsertUseCase',
#                'InsertClass',
#                'InsertPackage',
#                'separator',
#                'InsertAssociation',
#                'InsertDependency',
#                'InsertGeneralization',
#                'separator',
#                'InsertComment',
#                'InsertCommentLine'),
#            )


    def __init__(self):
        AbstractWindow.__init__(self)
        self.diagram = None

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        #self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.view

    def get_canvas(self):
        return self.diagram.canvas

    def set_diagram(self, diagram):
        if self.diagram:
            self.diagram.disconnect(self.__on_diagram_event)
            #self.diagram.canvas.disconnect(self.__undo_id)
            #self.diagram.canvas.disconnect(self.__snap_to_grid_id)
        self.diagram = diagram
        if self.get_state() == AbstractWindow.STATE_ACTIVE:
            self.get_window().set_title(diagram.name or 'NoName')
            self.view.set_diagram(diagram)
        if diagram:
            diagram.canvas.set_property ('allow_undo', 1)
            diagram.connect(('name', '__unlink__'), self.__on_diagram_event)
            self.__undo_id = diagram.canvas.connect('undo', self.__on_diagram_undo)
            #self.__snap_to_grid_id = diagram.canvas.connect('notify::snap-to-grid', self.__on_diagram_notify_snap_to_grid)
            # Set capabilities:
            self.__on_diagram_undo(diagram.canvas)

    def construct(self):
        self._check_state(AbstractWindow.STATE_INIT)
        title = self.diagram and self.diagram.name or 'NoName'

        table = gtk.Table(2,2, gtk.FALSE)
        table.set_row_spacings (4)
        table.set_col_spacings (4)

        frame = gtk.Frame()
        frame.set_shadow_type (gtk.SHADOW_IN)
        table.attach (frame, 0, 1, 0, 1,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        view = DiagramView (diagram=self.diagram)
        view.set_scroll_region(0, 0, 600, 450)

        frame.add (view)
        
        sbar = gtk.VScrollbar (view.get_vadjustment())
        table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
                      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

        sbar = gtk.HScrollbar (view.get_hadjustment())
        table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
                      gtk.FILL)

        view.connect('notify::tool', self.__on_view_notify_tool)
        view.connect_after('event-after', self.__on_view_event)
        view.connect('focus_item', self.__on_view_focus_item)
        view.connect('select_item', self.__on_view_select_item)
        view.connect('unselect_item', self.__on_view_select_item)
        self.view = view

        table.show_all()

        self._construct_window(name='diagram',
                               title=title,
                               size=(550, 550),
                               contents=table)
                               

    def _on_window_destroy(self, window):
        """Window is destroyed. Do the same thing that would
        be done if File->Close was pressed.
        """
        AbstractWindow._on_window_destroy(self, window)
        # Set diagram to None, so all refrences to the diagram are destroyed.
        self.set_diagram(None)
        del self.view
        del self.diagram

    def __on_view_notify_tool(self, view, tool):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        #print self, view, tool
        if not view.get_property('tool'):
            self.set_message('')

    def __on_view_event(self, view, event):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        # handle mouse button 3 (popup menu):
        if event.type == gtk.gdk.BUTTON_PRESS:
            # First push the undo stack...
            view.canvas.push_undo(None)

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            vitem = view.focus_item
            if vitem:
                item = vitem.item
                self._construct_popup_menu(menu_def=item.get_popup_menu(),
                                           event=event)
            return True
        return False

    def __on_view_focus_item(self, view, focus_item):
        self.execute_action('ItemFocus')
        #self.set_capability('focus', focus_item is not None)

    def __on_view_select_item(self, view, select_item):
        self.execute_action('ItemSelect')
        #self.set_capability('select', len (view.selected_items) > 0)

    def __on_diagram_undo(self, canvas):
        self.execute_action('EditUndoStack')
#        self.set_capability('undo', canvas.get_undo_depth() > 0)
#        self.set_capability('redo', canvas.get_redo_depth() > 0)

    def __on_diagram_event(self, element, pspec):
        if pspec == '__unlink__':
            self.close()
        else:
            try:
                if pspec.name == 'name':
                    self.get_window().set_title(self.diagram.name or '<None>')
            except:
                pass

import diagramactions
import gaphor.diagram.actions
