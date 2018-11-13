"""
The main application window.
"""

import logging
import os.path
from builtins import object
from builtins import str
from zope import component

from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import pkg_resources
from zope.interface import implementer

from gaphor import UML
# =======
# import gobject, gtk

# from zope import interface, component
# from gaphor.interfaces import IActionProvider
# from interfaces import IUIComponent

# from gaphor import UML
# from gaphor.core import _, inject, action, toggle_action, build_action_group, transactional
# from namespace import NamespaceModel, NamespaceView
# from diagramtab import DiagramTab
# from toolbox import Toolbox
# from diagramtoolbox import TOOLBOX_ACTIONS
# from toplevelwindow import ToplevelWindow


# from interfaces import IDiagramSelectionChange
# from gaphor.interfaces import IServiceEvent, IActionExecutedEvent
# >>>>>>> parent of 22d7dc07... Merge branch 'docking'
from gaphor.UML.event import ModelFactoryEvent
from gaphor.core import _, inject, action, toggle_action, open_action, build_action_group, transactional
from gaphor.interfaces import IService, IActionProvider
from gaphor.services.filemanager import FileManagerStateChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.accelmap import load_accel_map, save_accel_map
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.diagramtoolbox import TOOLBOX_ACTIONS
from gaphor.ui.event import DiagramTabChange, DiagramSelectionChange
from gaphor.ui.interfaces import IDiagramTabChange
from gaphor.ui.interfaces import IUIComponent
from gaphor.ui.namespace import NamespaceModel, NamespaceView
from gaphor.ui.toolbox import Toolbox as _Toolbox

log = logging.getLogger(__name__)

ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)


STATIC_MENU_XML = """
  <ui>
    <menubar name="mainwindow">
      <menu action="%s">
        <menuitem action="%s" />
      </menu>
    </menubar>
  </ui>
"""


@implementer(IService, IActionProvider)
class MainWindow(object):
    """
    The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """

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
        self.notebook_map = {}
        self._current_diagram_tab = None
        #self.layout = None
        # Tree view:
        self._tree_view = None


    def init(self, app=None):
        self.init_stock_icons()
        self.init_action_group()
        self.init_ui_components()


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
            a = Gtk.Action(name, label, None, None)
            a.set_property('hide-if-empty', False)
            self.action_group.add_action(a)
        self._tab_ui_settings = None
        self.action_group.get_action('diagram-drawing-style').set_active(self.properties('diagram.sloppiness', 0) != 0)

        self.action_manager.register_action_provider(self)


    tree_model = property(lambda s: s.tree_view.get_model())

    tree_view = property(lambda s: s._tree_view)


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
            dialog = Gtk.MessageDialog(self.window,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.NONE,
                    _('Save changed to your model before closing?'))
            dialog.format_secondary_text(
                    _('If you close without saving, your changes will be discarded.'))
            dialog.add_buttons('Close _without saving', Gtk.ResponseType.REJECT,
                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_SAVE, Gtk.ResponseType.YES)
            dialog.set_default_response(Gtk.ResponseType.YES)
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                # On filedialog.cancel, the application should not close.
                return self.file_manager.action_save()
            return response == Gtk.ResponseType.REJECT
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

        tab = DiagramTab(self)
        tab.set_diagram(diagram)
        widget = tab.construct()
        tab.set_drawing_style(self.properties('diagram.sloppiness', 0))
        self.add_tab(tab, widget, tab.title)
        self.set_current_page(tab)

        return tab


    def open(self):

        load_accel_map()

        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (GdkPixbuf.Pixbuf.new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(list(icons))

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        # Create a full featured window.
        vbox = Gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        menubar = self.ui_manager.get_widget(self.menubar_path)
        if menubar:
            vbox.pack_start(menubar, False, True, 0)

        toolbar = self.ui_manager.get_widget(self.toolbar_path)
        if toolbar:
            vbox.pack_start(toolbar, False, True, 0)

        model = NamespaceModel(self.element_factory)
        view = NamespaceView(model, self.element_factory)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.add(view)
        view.show()

        view.connect_after('event-after', self._on_view_event)
        view.connect('row-activated', self._on_view_row_activated)
        view.connect_after('cursor-changed', self._on_view_cursor_changed)

        vbox = Gtk.VBox()
        vbox.pack_start(scrolled_window, expand=True, padding=3)
        scrolled_window.show()

        paned = Gtk.HPaned()
        paned.set_property('position', 160)
        paned.pack1(vbox)
        vbox.show()

        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_show_border(False)

        notebook.connect_after('switch-page', self._on_notebook_switch_page)
        notebook.connect_after('page-removed', self._on_notebook_page_removed)

        paned.pack2(notebook)
        notebook.show()
        paned.show()

        self.notebook = notebook
        self._tree_view = view

        toolbox = Toolbox()
        toolbox_widget = toolbox.construct()
        vbox.pack_start(toolbox_widget, False, True, 0)

        self._toolbox = toolbox
        self._toolbox_widget = toolbox_widget

        self.open_welcome_page()

        self.window.show()

        self.window.connect('delete-event', self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_resizable(True)
        self.window.connect('size-allocate', self._on_window_size_allocate)
        self.window.connect('destroy', self._on_window_destroy)
        #self.window.connect_after('key-press-event', self._on_key_press_event)

        cr = self.component_registry
        cr.register_handler(self._on_file_manager_state_changed)
        cr.register_handler(self._on_undo_manager_state_changed)
        cr.register_handler(self._new_model_content)
        # TODO: register on ElementCreate/Delete event

        return paned



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

    def add_tab(self, tab, contents, label):
        """
        Create a new tab on the notebook with window as its contents.
        Returns: The page number of the tab.
        """
        self.notebook_map[contents] = tab
        #contents.connect('destroy', self._on_tab_destroy)
        l = Gtk.Label(label=label)

        #style = Gtk.RcStyle()
        #style.xthickness = 0
        #style.ythickness = 0
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        #button.modify_style(style)
        button.connect("clicked", self._on_tab_close_button_pressed, tab)

        close_image = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
        button.add(close_image)

        box = Gtk.HBox()
        box.pack_start(l, True, True, 0)
        box.pack_start(button, False, False)
        box.show_all()

        # Note: append_page() emits switch-page event
        self.notebook.append_page(contents, box)
        self.notebook.set_tab_reorderable(contents, True)
        page_num = self.notebook.page_num(contents)
        #self.notebook.set_current_page(page_num)
        return page_num

    def get_current_tab(self):
        """
        Return the window (DiagramTab) that is currently visible on the
        notebook.
        """
        current = self.notebook.get_current_page()
        content = self.notebook.get_nth_page(current)
        return self.notebook_map.get(content)

    def set_current_page(self, tab):
        """
        Force a specific tab (DiagramTab) to the foreground.
        """
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.set_current_page(num)
                return


    def set_tab_label(self, tab, label):
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                l = Gtk.Label(label=label)
                l.show()
                self.notebook.set_tab_label(p, l)

    def get_tabs(self):
        #tabs = [i.diagram_tab for i in self.layout.get_widgets('diagram-tab')]
        return self.notebook_map.values()

    def remove_tab(self, tab):
        """
        Remove the tab from the notebook. Tab is such a thing as
        a DiagramTab.
        """
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.remove_page(num)
                del self.notebook_map[p]
                return

    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = self.tree_model.path_from_element(element)
        # Expand the first row:
        if len(path) > 1:
            self._tree_view.expand_row(path[:-1], False)
        selection = self._tree_view.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self._tree_view)

    # Signal callbacks:

    @component.adapter(ModelFactoryEvent)
    def _new_model_content(self, event):
        """
        Open the toplevel element and load toplevel diagrams.
        """
        # TODO: Make handlers for ModelFactoryEvent from within the GUI obj
        for diagram in self.element_factory.select(lambda e: e.isKindOf(UML.Diagram) and not (e.namespace and e.namespace.namespace)):
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
        if GObject.main_depth() > 0:
            Gtk.main_quit()
        cr = self.component_registry
        cr.unregister_handler(self._on_undo_manager_state_changed)
        cr.unregister_handler(self._on_file_manager_state_changed)
        cr.unregister_handler(self._new_model_content)

    def _on_tab_close_button_pressed(self, event, tab):
        tab.close()

    def _on_tab_destroy(self, widget):
        tab = self.notebook_map[widget]
        assert isinstance(tab, DiagramTab)
        self.remove_tab(tab)

    def _on_window_delete(self, window = None, event = None):
        return not self.ask_to_close()

    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
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
        self.action_group.get_action('tree-view-create-diagram').props.sensitive = isinstance(element, UML.Package)
        self.action_group.get_action('tree-view-create-package').props.sensitive = isinstance(element, UML.Package)

        self.action_group.get_action('tree-view-delete-diagram').props.visible = isinstance(element, UML.Diagram)
        self.action_group.get_action('tree-view-delete-package').props.visible = isinstance(element, UML.Package) and not element.presentation

        self.action_group.get_action('tree-view-open').props.sensitive = isinstance(element, UML.Diagram)

    def _insensivate_toolbox(self):
        for button in self._toolbox_widget.buttons:
            button.set_property('sensitive', False)

    def _on_notebook_page_removed(self, notebook, tab, page_num):
        if self._tab_ui_settings:
            action_group, ui_id = self._tab_ui_settings
            self.ui_manager.remove_action_group(action_group)
            self.ui_manager.remove_ui(ui_id)
            self._tab_ui_settings = None
            if notebook.get_current_page() == -1:
                self._insensivate_toolbox()
            else:
                self._on_notebook_switch_page(notebook, None, notebook.get_current_page())

    def _on_notebook_switch_page(self, notebook, tab, page_num):
        """
        Another page (tab) is put on the front of the diagram notebook.
        A dummy action is executed.
        """
        if self._tab_ui_settings:
            action_group, ui_id = self._tab_ui_settings
            self.ui_manager.remove_action_group(action_group)
            self.ui_manager.remove_ui(ui_id)
            self._tab_ui_settings = None

        content = self.notebook.get_nth_page(page_num)
        tab = self.notebook_map.get(content)
        assert isinstance(tab, DiagramTab), str(tab)

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
        self.ask_to_close() and Gtk.main_quit()
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
        for button in self._toolbox_widget.buttons:

            action_name = button.action_name
            action = action_group.get_action(action_name)
            if action:
                action.connect_proxy(button)


Gtk.AccelMap.add_filter('gaphor')


@implementer(IUIComponent, IActionProvider)
class Namespace(object):

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
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
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
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
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
        self.action_group.get_action('tree-view-create-diagram').props.sensitive = isinstance(element, UML.Package)
        self.action_group.get_action('tree-view-create-package').props.sensitive = isinstance(element, UML.Package)

        self.action_group.get_action('tree-view-delete-diagram').props.visible = isinstance(element, UML.Diagram)
        self.action_group.get_action('tree-view-delete-package').props.visible = isinstance(element, UML.Package) and not element.presentation

        self.action_group.get_action('tree-view-open').props.sensitive = isinstance(element, UML.Diagram)


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
        if isinstance(element, UML.Diagram):
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
        diagram = self.element_factory.create(UML.Diagram)
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
        m = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.YES_NO,
                              'Do you really want to delete diagram %s?\n\n'
                              'This will possibly delete diagram items\n'
                              'that are not shown in other diagrams.'
                              % (diagram.name or '<None>'))
        if m.run() == Gtk.ResponseType.YES:
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
        package = self.element_factory.create(UML.Package)
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
        assert isinstance(package, UML.Package)
        package.unlink()


    @action(name='tree-view-refresh', label=_('_Refresh'))
    def tree_view_refresh(self):
        self._namespace.get_model().refresh()


@implementer(IUIComponent, IActionProvider)
class Toolbox(object):

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
        if event.get_state() & Gdk.ModifierType.SHIFT_MASK or \
                (event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK):
            keyval = Gdk.keyval_name(event.keyval)
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
