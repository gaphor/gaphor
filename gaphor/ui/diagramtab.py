#!/usr/bin/env python

import gtk
from cairo import Matrix

from zope import component
from gaphas.view import GtkView
from gaphor import UML
from gaphor.core import _, inject, transactional, action, build_action_group
from gaphor.application import Application
from gaphor.UML.interfaces import IAttributeChangeEvent, IElementDeleteEvent
from gaphor.diagram import get_diagram_item
from gaphor.diagram.items import DiagramItem
from gaphor.transaction import Transaction
from gaphor.ui.diagramtoolbox import DiagramToolbox
from event import DiagramSelectionChange

class DiagramTab(object):
    
    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="edit">
            <placeholder name="ternary">
              <menuitem action="diagram-delete" />
              <separator />
              <menuitem action="diagram-select-all" />
              <menuitem action="diagram-unselect-all" />
              <separator />
            </placeholder>
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
          <placeholder name="left">
            <separator />
            <toolitem action="diagram-zoom-in" />
            <toolitem action="diagram-zoom-out" />
            <toolitem action="diagram-zoom-100" />
          </placeholder>
        </toolbar>
      </ui>
    """

    VIEW_TARGET_STRING = 0
    VIEW_TARGET_ELEMENT_ID = 1
    VIEW_TARGET_TOOLBOX_ACTION = 2
    VIEW_DND_TARGETS = [
        ('gaphor/element-id', 0, VIEW_TARGET_ELEMENT_ID),
        ('gaphor/toolbox-action', 0, VIEW_TARGET_TOOLBOX_ACTION)]


    def __init__(self, owning_window):
        self.diagram = None
        self.view = None
        self.owning_window = owning_window
        self.action_group = build_action_group(self)
        self.toolbox = None
        Application.register_handler(self._on_element_change)
        Application.register_handler(self._on_element_delete)

    title = property(lambda s: s.diagram and s.diagram.name or _('<None>'))

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def get_canvas(self):
        return self.diagram.canvas

    def set_diagram(self, diagram):
        self.diagram = diagram

        if diagram and self.view:
            self.view.hadjustment.set_value(0.0)
            self.view.vadjustment.set_value(0.0)


    def construct(self):
        """
        Create the widget.
        
        Returns: the newly created widget.
        """
        assert self.diagram

        view = GtkView(canvas=self.diagram.canvas)
        view.drag_dest_set(gtk.DEST_DEFAULT_ALL, DiagramTab.VIEW_DND_TARGETS,
                           gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(view)
        scrolled_window.show_all()

        view.connect('focus-changed', self._on_view_selection_changed)
        view.connect('selection-changed', self._on_view_selection_changed)
        view.connect_after('key-press-event', self._on_key_press_event)
        view.connect('drag-data-received', self._on_drag_data_received)

        self.view = view

        self.widget = scrolled_window
        
        self.toolbox = DiagramToolbox(self.diagram, view)
        
        return scrolled_window


    @component.adapter(IAttributeChangeEvent)
    def _on_element_change(self, event):
        if event.element is self.diagram and \
                event.property is UML.Diagram.name:
           self.owning_window.set_tab_label(self, self.title) 


    @component.adapter(IElementDeleteEvent)
    def _on_element_delete(self, event):
        if event.element is self.diagram:
            self.close()


    @action(name='diagram-close', stock_id='gtk-close')
    def close(self):
        """
        Tab is destroyed. Do the same thing that would
        be done if File->Close was pressed.
        """
        self.owning_window.remove_tab(self)
        self.set_diagram(None)
        Application.unregister_handler(self._on_element_delete)
        Application.unregister_handler(self._on_element_change)
        del self.view


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
        for i in list(items):
            if isinstance(i, DiagramItem):
                i.unlink()
            else:
                if i.canvas:
                    i.canvas.remove(i)


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
            if event.keyval == gtk.keysyms.Delete and \
                    (event.state == 0 or event.state & gtk.gdk.MOD2_MASK):
                self.delete_selected_items()
            elif event.keyval == gtk.keysyms.BackSpace and \
                    (event.state == 0 or event.state & gtk.gdk.MOD2_MASK):
                self.delete_selected_items()


    def _on_view_selection_changed(self, view, selection_or_focus):
        Application.handle(DiagramSelectionChange(view, view.focused_item, view.selected_items))


    def _on_drag_data_received(self, view, context, x, y, data, info, time):
        """
        Handle data dropped on the canvas.
        """
        if data and data.format == 8 and info == DiagramTab.VIEW_TARGET_TOOLBOX_ACTION:
            tool = self.toolbox.get_tool(data.data)
            tool.create_item((x, y))
            context.finish(True, False, time)
        elif data and data.format == 8 and info == DiagramTab.VIEW_TARGET_ELEMENT_ID:
            #print 'drag_data_received:', data.data, info
            n, p = data.data.split('#')
            element = self.element_factory.lookup(n)
            assert element

            # TODO: use adapters to execute code below

            q = type(element)
            if p:
                q = q, p
            item_class = get_diagram_item(q)
            if isinstance(element, UML.Diagram):
                self.action_manager.execute('OpenModelElement')
            elif item_class:
                tx = Transaction()
                item = self.diagram.create(item_class)
                assert item
                
                x, y = view.get_matrix_v2i(item).transform_point(x, y)
                item.matrix.translate(x, y)
                item.subject = element
                tx.commit()
                view.unselect_all()
                view.focused_item = item

            else:
                log.warning('No graphical representation for UML element %s' % type(element).__name__)
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

# vim: sw=4:et:ai
