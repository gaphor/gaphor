#!/usr/bin/env python
# vim: sw=4:et

import gtk

from zope import component
from gaphor import UML
from gaphor.core import _, inject, transactional, action, build_action_group
from gaphor.diagram import get_diagram_item
from gaphor.transaction import Transaction
from gaphor.ui.diagramview import DiagramView
from gaphor.ui.diagramtoolbox import DiagramToolbox
from event import DiagramSelectionChange

class DiagramTab(object):
    
    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="edit">
            <menuitem action="diagram-delete" />
            <separator />
            <menuitem action="diagram-select-all" />
            <menuitem action="diagram-unselect-all" />
          </menu>
          <menu action="diagram">
            <placeholder name="secondary">
              <menuitem action="diagram-zoom-in" />
              <menuitem action="diagram-zoom-out" />
              <menuitem action="diagram-zoom-100" />
              <separator />
              <menuitem action="diagram-close" />
            </placeholder>
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
          <separator />
          <toolitem action="diagram-zoom-in" />
          <toolitem action="diagram-zoom-out" />
          <toolitem action="diagram-zoom-100" />
        </toolbar>
      </ui>
    """

    def __init__(self, owning_window):
        self.diagram = None
        self.view = None
        self.owning_window = owning_window
        self.action_group = build_action_group(self)
        self.toolbox = None

    title = property(lambda s: s.diagram and s.diagram.name or _('<None>'))

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

            if self.view:
                self.view.hadjustment.set_value(0.0)
                self.view.vadjustment.set_value(0.0)


    def construct(self):
        """
        Create the widget.
        
        Returns: the newly created widget.
        """
        assert self.diagram

        table = gtk.Table(2,2, False)

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

        view.connect('focus-changed', self._on_view_selection_changed)
        view.connect('selection-changed', self._on_view_selection_changed)
        view.connect_after('key-press-event', self._on_key_press_event)
        view.connect('drag-data-received', self._on_drag_data_received)

        self.view = view

        table.show_all()
        self.widget = table
        
        self.toolbox = DiagramToolbox(view)
        
        return table

    @action(name='diagram-close', stock_id='gtk-close')
    def close(self):
        """
        Tab is destroyed. Do the same thing that would
        be done if File->Close was pressed.
        """
        # Set diagram to None, so all refrences to the diagram are destroyed.
        #self.widget.destroy()

        self.owning_window.remove_tab(self)
        self.set_diagram(None)
        # We need this to get the view deleted properly:
        #del self.view.diagram
        del self.view
        del self.diagram

    @action(name='diagram-zoom-in', stock_id='gtk-zoom-in')
    def zoom_in(self):
        self.view.zoom(1.2)

    @action(name='diagram-zoom-out', stock_id='gtk-zoom-out')
    def zoom_out(self):
        self.view.zoom(1 / 1.2)

    @action(name='diagram-zoom-100', stock_id='gtk-zoom-100')
    def zoom_100(self):
        zx = self.view.matrix[0]
        self.view.zoom(1 / zx)

    @action(name='diagram-select-all', label='_Select all', accel='<Control>a')
    def select_all(self):
        self.view.select_all()

    @action(name='diagram-unselect-all', label='Des_elect all',
            accel='<Control><Shift>a')
    def unselect_all(self):
        self.view.unselect_all()
        
    @action(name='diagram-delete', stock_id='gtk-delete')
    @transactional
    def delete_selected_items(self):
        items = self.view.selected_items
        for i in items:
            s = i.subject
            if s and len(s.presentation) == 1:
                s.unlink()
            i.unlink()

    def may_remove_from_model(self, view):
        """
        Check if there are items which will be deleted from the model
        (when their last views are deleted). If so request user
        confirmation before deletion.
        """
        items = self.view.selected_items
        last_in_model = filter(lambda i: i.subject and len(i.subject.presentation) == 1, items)
        log.debug('Last in model: %s' % str(last_in_model))
        if last_in_model:
            return self.confirm_deletion_of_items(last_in_model)
        return True

    def confirm_deletion_of_items(self, last_in_model):
        """
        Request user confirmation on deleting the item from the model.
        """
        s = ''
        for item in last_in_model:
            s += '%s\n' % str(item)

        dialog = gtk.MessageDialog(
                None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_YES_NO,
                'This will remove the following selected items from the model:\n%s\nAre you sure?' % s
                )
        dialog.set_transient_for(self.owning_window.window)
        value = dialog.run()
        dialog.destroy()
        if value == gtk.RESPONSE_YES:
            return True
        return False

    def _on_key_press_event(self, view, event):
        """
        Handle the 'Delete' key. This can not be handled directly (through
        GTK's accelerators) since otherwise this key will confuse the text
        edit stuff.
        """
        if view.is_focus():
            if event.keyval == 0xFFFF and event.state == 0: # Delete
                self.delete_selected_items()
            elif event.keyval == 0xFF08 and event.state == 0: # Backspace
                self.delete_selected_items()
            else:
                print '%x' %event.keyval, event.state
                #self.action_manager.execute('diagram-delete')


    def _on_view_selection_changed(self, view, selection_or_focus):
        component.handle(DiagramSelectionChange(view, view.focused_item, view.selected_items))

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
                self.action_manager.execute('OpenModelElement')
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

            else:
                log.warning('No graphical representation for UML element %s' % type(element).__name__)
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

