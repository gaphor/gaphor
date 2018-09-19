#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         slmm <noreply@example.com>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
The main application window.
"""

from __future__ import absolute_import
import os.path
import gobject, gtk
from logging import getLogger

import pkg_resources
from zope import interface, component
from gaphor.interfaces import IService, IActionProvider
from .interfaces import IUIComponent

from etk.docking import DockLayout

from gaphor.UML import uml2
from gaphor.core import _, inject, action, toggle_action, open_action, build_action_group, transactional
from .namespace import NamespaceModel, NamespaceView
from .diagramtab import DiagramTab
from .toolbox import Toolbox as _Toolbox
from .diagramtoolbox import TOOLBOX_ACTIONS
from etk.docking import DockItem, DockGroup, add_new_group_left, add_new_group_right, \
        add_new_group_above, add_new_group_below, add_new_group_floating, settings
from .layout import deserialize

from .interfaces import IDiagramTabChange
from gaphor.UML.event import ModelFactoryEvent
from .event import DiagramTabChange, DiagramSelectionChange
from gaphor.services.filemanager import FileManagerStateChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.accelmap import load_accel_map, save_accel_map

logger = getLogger(name='MainWindow')

ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)

settings['diagrams'].expand = True
settings['diagrams'].auto_remove = False
settings['diagrams'].inherit_settings = False
settings['EtkDockGroup'].expand = False
settings['EtkDockPaned'].expand = False

STATIC_MENU_XML = """
  <ui>
    <menubar name="mainwindow">
      <menu action="%s">
        <menuitem action="%s" />
      </menu>
    </menubar>
  </ui>
"""


class MainWindow(object):
    """
    The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """
    interface.implements(IService, IActionProvider)


    component_registry = inject('component_registry')
    properties = inject('properties')
    element_factory = inject('element_factory')
    action_manager = inject('action_manager')
    file_manager = inject('file_manager')
    ui_manager = inject('ui_manager')

    title = 'Gaphor'
    size = property(lambda s: s.properties.get('ui.window-size', (760, 580)))
    menubar_path = '/mainwindow'
    toolbar_path = '/mainwindow-toolbar'
    resizable = True

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary" />
            <separator />
            <menu action="file-export" />
            <menu action="file-import" />
            <separator />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
            <separator />
            <menuitem action="file-quit" />
          </menu>
          <menu action="edit">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="diagram">
            <menuitem action="diagram-drawing-style" />
            <separator />
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="tools">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="window">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="help">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
            <placeholder name="left" />
            <separator expand="true" />
            <placeholder name="right" />
        </toolbar>
      </ui>
    """

    def __init__(self):
        self.window = None
        self.model_changed = False

        # Map tab contents to DiagramTab
        #self.notebook_map = {}
        self._current_diagram_tab = None
        self.layout = None


    def init(self, app=None):
        #self.init_pygtk()
        self.init_stock_icons()
        self.init_action_group()
        self.init_ui_components()


    def init_pygtk(self):
        """
        Make sure we have GTK+ >= 2.0
        """
        import pygtk
        pygtk.require('2.0')
        del pygtk


    def init_stock_icons(self):
        # Load stock items
        import gaphor.ui.stock
        gaphor.ui.stock.load_stock_icons()


    def init_ui_components(self):
        component_registry = self.component_registry
        for ep in pkg_resources.iter_entry_points('gaphor.uicomponents'):
            log.debug('found entry point uicomponent.%s' % ep.name)
            cls = ep.load()
            if not IUIComponent.implementedBy(cls):
                raise NameError('Entry point %s doesn''t provide IUIComponent' % ep.name)
            uicomp = cls()
            uicomp.ui_name = ep.name
            component_registry.register_utility(uicomp, IUIComponent, ep.name)
            if IActionProvider.providedBy(uicomp):
                self.action_manager.register_action_provider(uicomp)
                

    def shutdown(self):
        if self.window:
            self.window.destroy()
            self.window = None
        save_accel_map()

        cr = self.component_registry
        cr.unregister_handler(self._on_file_manager_state_changed)
        cr.unregister_handler(self._on_undo_manager_state_changed)
        cr.unregister_handler(self._new_model_content)
        #self.ui_manager.remove_action_group(self.action_group)


    def init_action_group(self):
        self.action_group = build_action_group(self)
        for name, label in (('file', '_File'),
                            ('file-export', '_Export'),
                            ('file-import', '_Import'),
                            ('edit', '_Edit'),
                            ('diagram', '_Diagram'),
                            ('tools', '_Tools'),
                            ('window', '_Window'),
                            ('help', '_Help')):
            a = gtk.Action(name, label, None, None)
            a.set_property('hide-if-empty', False)
            self.action_group.add_action(a)
        self._tab_ui_settings = None
        self.action_group.get_action('diagram-drawing-style').set_active(self.properties('diagram.sloppiness', 0) != 0)

        self.action_manager.register_action_provider(self)


    def get_filename(self):
        """
        Return the file name of the currently opened model.
        """
        return self.file_manager.filename


    def get_current_diagram_tab(self):
        """
        Get the currently opened and viewed DiagramTab, shown on the right
        side of the main window.
        See also: get_current_diagram(), get_current_diagram_view().
        """
        return self._current_diagram_tab


    def get_current_diagram(self):
        """
        Return the Diagram associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram_view().
        """
        tab = self._current_diagram_tab
        return tab and tab.get_diagram()


    def get_current_diagram_view(self):
        """
        Return the DiagramView associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram().
        """
        tab = self._current_diagram_tab
        return tab and tab.get_view()


    def ask_to_close(self):
        """
        Ask user to close window if the model has changed.
        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """
        if self.model_changed:
            dialog = gtk.MessageDialog(self.window,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_NONE,
                    _('Save changed to your model before closing?'))
            dialog.format_secondary_text(
                    _('If you close without saving, your changes will be discarded.'))
            dialog.add_buttons('Close _without saving', gtk.RESPONSE_REJECT,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_SAVE, gtk.RESPONSE_YES)
            dialog.set_default_response(gtk.RESPONSE_YES)
            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_YES:
                # On filedialog.cancel, the application should not close.
                return self.file_manager.action_save()
            return response == gtk.RESPONSE_REJECT
        return True


    def show_diagram(self, diagram):
        """
        Show a Diagram element in a new tab.
        If a tab is already open, show that one instead.
        """
        # Try to find an existing window/tab and let it get focus:
        for tab in self.get_tabs():
            if tab.get_diagram() is diagram:
                self.set_current_page(tab)
                return tab

        tab = DiagramTab(diagram)
        dock_item = tab.construct()
        dock_item.set_name('diagram-tab')
        dock_item.diagram_tab = tab
        assert dock_item.get_name() == 'diagram-tab'
        tab.set_drawing_style(self.properties('diagram.sloppiness', 0))

        self.add_tab(dock_item)

        return tab


    def open(self):

        load_accel_map()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (gtk.gdk.pixbuf_new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        
        # Create a full featured window.
        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        menubar = self.ui_manager.get_widget(self.menubar_path)
        if menubar:
            vbox.pack_start(menubar, expand=False)
        
        toolbar = self.ui_manager.get_widget(self.toolbar_path)
        if toolbar:
            vbox.pack_start(toolbar, expand=False)

        def _factory(name):
            comp = self.component_registry.get_utility(IUIComponent, name)
            logger.debug('open component %s' % str(comp))
            return comp.open()

        filename = pkg_resources.resource_filename('gaphor.ui', 'layout.xml')
        self.layout = DockLayout()

        with open(filename) as f:
            deserialize(self.layout, vbox, f.read(), _factory)
        
        self.layout.connect('item-closed', self._on_item_closed)
        self.layout.connect('item-selected', self._on_item_selected)

        vbox.show()
        # TODO: add statusbar

        self.window.show()

        self.window.connect('delete-event', self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_property('allow-shrink', True)
        self.window.connect('size-allocate', self._on_window_size_allocate)
        self.window.connect('destroy', self._on_window_destroy)
        #self.window.connect_after('key-press-event', self._on_key_press_event)

        cr = self.component_registry
        cr.register_handler(self._on_file_manager_state_changed)
        cr.register_handler(self._on_undo_manager_state_changed)
        cr.register_handler(self._new_model_content)
        # TODO: register on ElementCreate/Delete event


    def open_welcome_page(self):
        """
        Create a new tab with a textual welcome page, a sort of 101 for
        Gaphor.
        """
        pass

    def set_title(self):
        """
        Sets the window title.
        """
        filename = self.file_manager.filename
        if self.window:
            if filename:
                title = '%s - %s' % (self.title, filename)
            else:
                title = self.title
            if self.model_changed:
                title += ' *'
            self.window.set_title(title)


    # Notebook methods:

    def add_tab(self, item):
        """
        Create a new tab on the notebook with window as its contents.
        Returns: The page number of the tab.
        """
        group = list(self.layout.get_widgets('diagrams'))[0]
        group.insert_item(item)
        item.show_all()
        #item.diagram_tab = tab
        #self.notebook_map[item] = tab

    def set_current_page(self, tab):
        """
        Force a specific tab (DiagramTab) to the foreground.
        """
        for i in self.layout.get_widgets('diagram-tab'):
            if i.diagram_tab is tab:
                g = i.get_parent()
                g.set_current_item(g.item_num(i))
                return
        #for p, t in self.notebook_map.iteritems():
        #    if tab is t:
        #        num = self.notebook.page_num(p)
        #        self.notebook.set_current_page(num)
        #        return
        pass


    def get_tabs(self):
        tabs = [i.diagram_tab for i in self.layout.get_widgets('diagram-tab')]
        return tabs

    # Signal callbacks:

    @component.adapter(ModelFactoryEvent)
    def _new_model_content(self, event):
        """
        Open the toplevel element and load toplevel diagrams.
        """
        # TODO: Make handlers for ModelFactoryEvent from within the GUI obj
        for diagram in self.element_factory.select(lambda e: e.isKindOf(uml2.Diagram) and not (e.namespace and e.namespace.namespace)):
            self.show_diagram(diagram)
    

    @component.adapter(FileManagerStateChanged)
    def _on_file_manager_state_changed(self, event):
        # We're only interested in file operations
        if event.service is self.file_manager:
            self.model_changed = False
            self.set_title()


    @component.adapter(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event):
        """
        """
        undo_manager = event.service
        if not self.model_changed and undo_manager.can_undo():
            self.model_changed = True
            self.set_title()


    def _on_window_destroy(self, window):
        """
        Window is destroyed... Quit the application.
        """
        self.window = None
        if gobject.main_depth() > 0:
            gtk.main_quit()
        cr = self.component_registry
        cr.unregister_handler(self._on_undo_manager_state_changed)
        cr.unregister_handler(self._on_file_manager_state_changed)
        cr.unregister_handler(self._new_model_content)

    def _on_window_delete(self, window = None, event = None):
        return not self.ask_to_close()

    def _clear_ui_settings(self):
        try:
            ui_manager = self.ui_manager
        except component.ComponentLookupError as e:
            log.warning('No UI manager service found')
        else:
            if self._tab_ui_settings:
                action_group, ui_id = self._tab_ui_settings
                self.ui_manager.remove_action_group(action_group)
                self.ui_manager.remove_ui(ui_id)
                self._tab_ui_settings = None

    def _on_item_closed(self, layout, group, item):
        self._clear_ui_settings()
        try:
            ui_component = item.ui_component
        except AttributeError:
            log.warning('No ui component defined on item')
        else:
            ui_component.close()
        item.destroy()

    def _on_item_selected(self, layout, group, item):
        """
        Another page (tab) is put on the front of the diagram notebook.
        A dummy action is executed.
        """
        # TODO: Here the magic happens!
        # TODO: Need to see what the active view is, or make toolbox actions global
        self._clear_ui_settings()

        # Is it a diagram view?
        try:
            tab = item.diagram_tab
        except AttributeError:
            # Not a diagram tab
            return

        self._current_diagram_tab = tab

        #content = self.notebook.get_nth_page(page_num)
        #tab = self.notebook_map.get(content)
        #assert isinstance(tab, DiagramTab), str(tab)
        
        self.ui_manager.insert_action_group(tab.action_group, -1)
        ui_id = self.ui_manager.add_ui_from_string(tab.menu_xml)
        self._tab_ui_settings = tab.action_group, ui_id
        log.debug('Menus updated with %s, %d' % self._tab_ui_settings)

        # Make sure everyone knows the selection has changed.
        self.component_registry.handle(DiagramTabChange(item), DiagramSelectionChange(tab.view, tab.view.focused_item, tab.view.selected_items))


    def _on_window_size_allocate(self, window, allocation):
        """
        Store the window size in a property.
        """
        self.properties.set('ui.window-size', (allocation.width, allocation.height))


    # Actions:

    @action(name='file-quit', stock_id='gtk-quit')
    def quit(self):
        # TODO: check for changes (e.g. undo manager), fault-save
        self.ask_to_close() and gtk.main_quit()
        self.shutdown()


    @toggle_action(name='diagram-drawing-style', label='Hand drawn style', active=False)
    def hand_drawn_style(self, active):
        """
        Toggle between straight diagrams and "hand drawn" diagram style.
        """
        if active:
            sloppiness = 0.5
        else:
            sloppiness = 0.0
        for tab in self.get_tabs():
            tab.set_drawing_style(sloppiness)
        self.properties.set('diagram.sloppiness', sloppiness)


    def create_item(self, ui_component): #, widget, title, placement=None):
        """
        Create an item for a ui component. This method can be called from UIComponents.
        """
        item = DockItem(ui_component.title)
        item.add(ui_component.open())
        group = DockGroup()
        group.insert_item(item)
        placement = ui_component.placement
        if placement:
            if placement == 'floating':
                add_new_group_floating(group, self.layout, ui_component.size)
            else:
                location = self.layout.get_widgets(placement[1])[0]
                { 'left': add_new_group_left,
                  'right': add_new_group_right,
                  'above': add_new_group_above,
                  'below': add_new_group_below }[placement[0]](location, group)
        else:
            add_new_group_floating(group)
        item.show()
        item.ui_component = ui_component
        group.show()


gtk.accel_map_add_filter('gaphor')



class Namespace(object):

    interface.implements(IUIComponent, IActionProvider)

    title = _('Namespace')
    placement = ('left', 'diagrams')

    component_registry = inject('component_registry')
    element_factory = inject('element_factory')
    ui_manager = inject('ui_manager')
    action_manager = inject('action_manager')
    main_window = inject('main_window')

    menu_xml = STATIC_MENU_XML % ('window', 'open-namespace')

    _menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator />
            <menuitem action="tree-view-create-diagram" />
            <menuitem action="tree-view-create-package" />
            <separator />
            <menuitem action="tree-view-delete-diagram" />
            <menuitem action="tree-view-delete-package" />
            <separator />
          </menu>
        </menubar>
        <popup action="namespace-popup">
          <menuitem action="tree-view-open" />
          <menuitem action="tree-view-rename" />
          <separator />
          <menuitem action="tree-view-create-diagram" />
          <menuitem action="tree-view-create-package" />
          <separator />
          <menuitem action="tree-view-delete-diagram" />
          <menuitem action="tree-view-delete-package" />
          <separator />
          <menuitem action="tree-view-refresh" />
        </popup>
      </ui>
    """
    def __init__(self):
        self._namespace = None
        self._ui_id = None
        self.action_group = build_action_group(self)


    @open_action(name='open-namespace', label=_('_Namespace'))
    def open_namespace(self):
        if not self._namespace:
            #self.main_window.create_item(self) #self.open(), self.title, self.placement)
            return self
        else:
            self._namespace.set_property('has-focus', True)

    def open(self):
        widget = self.construct()
        self.component_registry.register_handler(self.expand_root_nodes)
        return widget


    def close(self):
        if self._namespace:
            self._namespace.destroy()
            self._namespace = None

            # TODO: How to ensure stuff is removed properly from services?
            #self.ui_manager.remove_ui(self._ui_id)
        self.component_registry.unregister_handler(self.expand_root_nodes)


    def construct(self):
        self._ui_id = self.ui_manager.add_ui_from_string(self._menu_xml)

        model = NamespaceModel(self.element_factory)
        view = NamespaceView(model, self.element_factory)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(view)
        scrolled_window.show()
        view.show()
        
        view.connect_after('event-after', self._on_view_event)
        view.connect('row-activated', self._on_view_row_activated)
        view.connect_after('cursor-changed', self._on_view_cursor_changed)
        view.connect('destroy', self._on_view_destroyed)
        self._namespace = view
        self.expand_root_nodes()

        return scrolled_window
      

    @component.adapter(ModelFactoryEvent)
    def expand_root_nodes(self, event=None):
        """
        """
        # Expand all root elements:
        self._namespace.expand_root_nodes()
        self._on_view_cursor_changed(self._namespace)


    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.ui_manager.get_widget('/namespace-popup')
            menu.popup(None, None, None, event.button, event.time)


    def _on_view_row_activated(self, view, path, column):
        """
        Double click on an element in the tree view.
        """
        self.action_manager.execute('tree-view-open')


    def _on_view_cursor_changed(self, view):
        """
        Another row is selected, execute a dummy action.
        """
        element = view.get_selected_element()
        self.action_group.get_action('tree-view-create-diagram').props.sensitive = isinstance(element, uml2.Package)
        self.action_group.get_action('tree-view-create-package').props.sensitive = isinstance(element, uml2.Package)

        self.action_group.get_action('tree-view-delete-diagram').props.visible = isinstance(element, uml2.Diagram)
        self.action_group.get_action('tree-view-delete-package').props.visible = isinstance(element, uml2.Package) and not element.presentation

        self.action_group.get_action('tree-view-open').props.sensitive = isinstance(element, uml2.Diagram)


    def _on_view_destroyed(self, widget):
        self.close()


    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = self._namespace.get_model().path_from_element(element)
        # Expand the first row:
        if len(path) > 1:
            self._namespace.expand_row(path[:-1], False)
        selection = self._namespace.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self._namespace)


    @action(name='tree-view-open', label='_Open')
    def tree_view_open_selected(self):
        element = self._namespace.get_selected_element()
        # TODO: Candidate for adapter?
        if isinstance(element, uml2.Diagram):
            self.main_window.show_diagram(element)
        else:
            log.debug('No action defined for element %s' % type(element).__name__)


    @action(name='tree-view-rename', label=_('Rename'), accel='F2')
    def tree_view_rename_selected(self):
        view = self._namespace
        element = view.get_selected_element()
        path = view.get_model().path_from_element(element)
        column = view.get_column(0)
        cell = column.get_cell_renderers()[1]
        cell.set_property('editable', 1)
        cell.set_property('text', element.name)
        view.set_cursor(path, column, True)
        cell.set_property('editable', 0)


    @action(name='tree-view-create-diagram', label=_('_New diagram'), stock_id='gaphor-diagram')
    @transactional
    def tree_view_create_diagram(self):
        element = self._namespace.get_selected_element()
        diagram = self.element_factory.create(uml2.Diagram)
        diagram.package = element

        if element:
            diagram.name = '%s diagram' % element.name
        else:
            diagram.name = 'New diagram'

        self.select_element(diagram)
        self.main_window.show_diagram(diagram)
        self.tree_view_rename_selected()


    @action(name='tree-view-delete-diagram', label=_('_Delete diagram'), stock_id='gtk-delete')
    @transactional
    def tree_view_delete_diagram(self):
        diagram = self._namespace.get_selected_element()
        m = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
                              gtk.BUTTONS_YES_NO,
                              'Do you really want to delete diagram %s?\n\n'
                              'This will possibly delete diagram items\n'
                              'that are not shown in other diagrams.'
                              % (diagram.name or '<None>'))
        if m.run() == gtk.RESPONSE_YES:
            for i in reversed(diagram.canvas.get_all_items()):
                s = i.subject
                if s and len(s.presentation) == 1:
                    s.unlink()
                i.unlink
            diagram.unlink()
        m.destroy()


    @action(name='tree-view-create-package', label=_('New _package'), stock_id='gaphor-package')
    @transactional
    def tree_view_create_package(self):
        element = self._namespace.get_selected_element()
        package = self.element_factory.create(uml2.Package)
        package.package = element

        if element:
            package.name = '%s package' % element.name
        else:
            package.name = 'New model'

        self.select_element(package)
        self.tree_view_rename_selected()


    @action(name='tree-view-delete-package', label=_('Delete pac_kage'), stock_id='gtk-delete')
    @transactional
    def tree_view_delete_package(self):
        package = self._namespace.get_selected_element()
        assert isinstance(package, uml2.Package)
        package.unlink()


    @action(name='tree-view-refresh', label=_('_Refresh'))
    def tree_view_refresh(self):
        self._namespace.get_model().refresh()



class Toolbox(object):

    interface.implements(IUIComponent, IActionProvider)

    title = _('Toolbox')
    placement = ('left', 'diagrams')

    component_registry = inject('component_registry')
    main_window = inject('main_window')
    properties = inject('properties')

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator/>
            <menuitem action="reset-tool-after-create" />
            <separator/>
          </menu>
          <menu action="window">
            <menuitem action="open-toolbox" />
          </menu>
        </menubar>
      </ui>
    """
    
    def __init__(self):
        self._toolbox = None
        self.action_group = build_action_group(self)
        self.action_group.get_action('reset-tool-after-create').set_active(self.properties.get('reset-tool-after-create', True))


    @open_action(name='open-toolbox', label=_('T_oolbox'))
    def open_toolbox(self):
        if not self._toolbox:
            #self.main_window.create_item(self) #.open(), self.title, self.placement)
            return self
        else:
            self._toolbox.set_property('has-focus', True)

    def open(self):
        widget = self.construct()
        self.main_window.window.connect_after('key-press-event', self._on_key_press_event)

        self.component_registry.register_handler(self._on_diagram_tab_change)
        if self.main_window.get_current_diagram_tab():
            self.update_toolbox(self.main_window.get_current_diagram_tab().toolbox.action_group)
        return widget

    def close(self):
        if self._toolbox:
            self.component_registry.unregister_handler(self._on_diagram_tab_change)
            self._toolbox.destroy()
            self._toolbox = None


    def construct(self):
        toolbox = _Toolbox(TOOLBOX_ACTIONS)
        toolbox.show()

        toolbox.connect('destroy', self._on_toolbox_destroyed)
        self._toolbox = toolbox
        return toolbox


    def _on_key_press_event(self, view, event):
        """
        Grab top level window events and select the appropriate tool based on the event.
        """
        if event.state & gtk.gdk.SHIFT_MASK or \
	        (event.state == 0 or event.state & gtk.gdk.MOD2_MASK):
            keyval = gtk.gdk.keyval_name(event.keyval)
            self.set_active_tool(shortcut=keyval)


    def _on_toolbox_destroyed(self, widget):
        self._toolbox = None


    @toggle_action(name='reset-tool-after-create', label=_('_Reset tool'), active=False)
    def reset_tool_after_create(self, active):
        self.properties.set('reset-tool-after-create', active)


    #def _insensivate_toolbox(self):
    #    for button in self._toolbox.buttons:
    #        button.set_property('sensitive', False)

    @component.adapter(IDiagramTabChange)
    def _on_diagram_tab_change(self, event):
        self.update_toolbox(event.diagram_tab.toolbox.action_group)

    def update_toolbox(self, action_group):
        """
        Update the buttons in the toolbox. Each button should be connected
        by an action. Each button is assigned a special _action_name_
        attribute that can be used to fetch the action from the ui manager.
        """
        if not self._toolbox:
            return

        for button in self._toolbox.buttons:
            
            action_name = button.action_name
            action = action_group.get_action(action_name)
            if action:
                action.connect_proxy(button)


    def set_active_tool(self, action_name=None, shortcut=None):
        """
        Set the tool based on the name of the action
        """
        # HACK:
        toolbox = self._toolbox
        if shortcut and toolbox:
            action_name = toolbox.shortcuts.get(shortcut)
            log.debug('Action for shortcut %s: %s' % (shortcut, action_name))
            if not action_name:
                return

        self.main_window.get_current_diagram_tab().toolbox.action_group.get_action(action_name).activate()
            

# vim:sw=4:et:ai
