
# vim:sw=4:et

import gtk
import namespace
import gaphor
import gaphor.UML as UML
from gaphor.i18n import _
from abstractwindow import AbstractWindow
from diagramtab import DiagramTab
from toolbox import Toolbox

# Load actions
import mainactions, diagramactions

class MainWindow(AbstractWindow):
    """The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """

    menu = (_('_File'), (
                'FileNew',
                'FileOpen',
                _('Recent files'), (
                    _('To be implemented'),),
                '<FileOpenSlot>',
                'separator',
                'FileSave',
                'FileSaveAs',
                '<FileSaveSlot>',
                'separator',
                _('_Import'), (
                    '<FileImportSlot>',),
                _('_Export'), (
                    'FileExportSVG',
                    '<FileExportSlot>'),
                'separator',
                'FileCloseTab',
                '<FileSlot>',
                'separator',
                'FileQuit'),
            _('_Edit'), (
                'EditUndo',
                'EditRedo',
                'separator',
                'EditDelete',
                'separator',
                'EditSelectAll',
                'EditDeselectAll',
                '<EditSlot>'),
            _('_Diagram'), (
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100',
                'separator',
                'SnapToGrid',
                'ShowGrid',
                'separator',
                'CreateDiagram',
                'DeleteDiagram',
                '<DiagramSlot>'),
            _('_Window'), (
                'OpenEditorWindow',
                'OpenConsoleWindow',
                '<WindowSlot>'),
            _('_Help'), (
                'About',
                '<HelpSlot>')
            )

    toolbar =  ('FileOpen',
                'separator',
                'FileSave',
                'FileSaveAs',
                'separator',
                'EditUndo',
                'EditRedo',
                'separator',
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100')

    toolbox = [
        ("", (
                'Pointer',
                'InsertComment',
                'InsertCommentLine')),
        (_("Classes"), (
                'InsertClass',
                'InsertInterface',
                'InsertPackage',
                'InsertAssociation',
                'InsertDependency',
                'InsertGeneralization',
                'InsertImplementation')),
        (_("Actions"), (
                'InsertAction',
                'InsertInitialNode',
                'InsertActivityFinalNode',
                'InsertDecisionNode',
                'InsertFlow')),
        (_("Components"), (
                'InsertComponent',)),
        (_("Use Cases"), (
                'InsertUseCase',
                'InsertActor',
                'InsertUseCaseAssociation',
                'InsertInclude',
                'InsertExtend')),
        (_("Profiles"), (
                'InsertProfile',
                'InsertMetaClass',
                'InsertStereotype',
                'InsertExtension')),
    ]
    ns_popup = ('RenameModelElement',
                'OpenModelElement',
                'separator',
                'CreateDiagram',
                'DeleteDiagram',
                'separator',
                'RefreshNamespaceModel',
                '<NamespacePopupSlot>')

    def __init__(self):
        AbstractWindow.__init__(self)
        self.__filename = None
        #self.__transient_windows = []
        self.notebook_map = {}

    def get_model(self):
        """Return the gtk.TreeModel associated with the main window
        (shown on the left side in a TreeView).
        """
        self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.model

    def get_tree_view(self):
        """Get the gtk.TreeView widget that visualized the TreeModel.
        See also get_model().
        """
        return self.view

    def set_filename(self, filename):
        """Set the file name of the currently opened model.
        """
        self.__filename = filename

    def get_filename(self):
        """Return the file name of the currently opened model.
        """
        return self.__filename

#    def get_transient_windows(self):
#        """Get the windows that act as child windows of the main window.
#        """
#        return self.__transient_windows

    def get_current_diagram_tab(self):
        """Get the currently opened and viewed DiagramTab, shown on the right
        side of the main window.
        See also: get_current_diagram(), get_current_diagram_view().
        """
        return self.get_current_tab()

    def get_current_diagram(self):
        """Return the Diagram associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram_view().
        """
        tab = self.get_current_diagram_tab()
        return tab and tab.get_diagram()

    def get_current_diagram_view(self):
        """Return the DiagramView associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram().
        """
        tab = self.get_current_diagram_tab()
        return tab and tab.get_view()

    def show_diagram(self, diagram):
        """Show a Diagram element in a new tab. If a tab is already open,
        show that one instead.
        """
        # Try to find an existing window/tab and let it get focus:
        for tab in self.get_tabs():
            if tab.get_diagram() is diagram:
                self.set_current_page(tab)
                return tab

        tab = DiagramTab(self)
        tab.set_diagram(diagram)
        tab.construct()
        return tab

    def construct(self):
        """Create the widgets that make up the main window.
        """
        model = namespace.NamespaceModel(gaphor.resource(UML.ElementFactory))
        view = namespace.NamespaceView(model)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(view)
        
        view.connect_after('event-after', self.on_view_event)
        view.connect('row-activated', self.on_view_row_activated)
        view.connect_after('cursor-changed', self.on_view_cursor_changed)

        vbox = gtk.VBox()
        vbox.pack_start(scrolled_window, expand=True)

        paned = gtk.HPaned()
        paned.set_property('position', 160)
        paned.pack1(vbox)
        notebook = gtk.Notebook()
        #notebook.popup_enable()
        notebook.set_scrollable(True)
        notebook.set_show_border(False)
 
        notebook.connect_after('switch-page', self.on_notebook_switch_page)

        paned.pack2(notebook)
        paned.show_all()

        self.notebook = notebook
        self.model = model
        self.view = view

        self._construct_window(name='main',
                               title='Gaphor',
                               size=(760, 580),
                               contents=paned)

        vbox.set_border_width(3)

        toolbox = Toolbox(self.menu_factory, self.toolbox)
        toolbox.construct()
        vbox.pack_start(toolbox, expand=False)
        toolbox.show()

        self._toolbox = toolbox

    def add_transient_window(self, window):
        """Add a window as a sub-window of the main application.
        """
        # Assign the window the accelerators od the main window too
        pass #window.get_window().add_accel_group(self.accel_group)
        #self.__transient_windows.append(window)
        #window.connect(self.on_transient_window_closed)

    # Notebook methods:

    def new_tab(self, window, contents, label):
        """Create a new tab on the notebook with window as its contents.
        Returns: The page number of the tab.
        """
        #contents = tab.get_contents()
        l = gtk.Label(label)
        #img = gtk.Image()
        #img.set_from_stock('gtk-close', gtk.ICON_SIZE_MENU)
        #b = gtk.Button()
        #b.set_border_width(0)
        #b.add(img)
        #h = gtk.HBox()
        #h.set_spacing(4)
        #h.pack_start(l, expand=False)
        #h.pack_start(b, expand=False)
        #h.show_all()
        self.notebook.append_page(contents, l)
        page_num = self.notebook.page_num(contents)
        self.notebook.set_current_page(page_num)
        self.notebook_map[contents] = window
        self.execute_action('TabChange')
        return page_num

    def get_current_tab(self):
        """Return the window (DiagramTab) that is currently visible on the
        notebook.
        """
        current = self.notebook.get_current_page()
        content = self.notebook.get_nth_page(current)
        return self.notebook_map.get(content)

    def set_current_page(self, tab):
        """Force a specific tab (DiagramTab) to the foreground.
        """
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.set_current_page(num)
                return

    def set_tab_label(self, tab, label):
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                l = gtk.Label(label)
                l.show()
                self.notebook.set_tab_label(p, l)

    def get_tabs(self):
        return self.notebook_map.values()

    def remove_tab(self, tab):
        """Remove the tab from the notebook. Tab is such a thing as
        a DiagramTab.
        """
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.remove_page(num)
                del self.notebook_map[p]
                self.execute_action('TabChange')
                return

    def select_element(self, element):
        """Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = self.get_model().path_from_element(element)
        # Expand the first row:
        self.get_tree_view().expand_row(path[:-1], False)
        # Select the diagram, so it can be opened by the OpenModelElement action
        selection = self.get_tree_view().get_selection()
        selection.select_path(path)
        self.execute_action('SelectRow')

    # Signal callbacks:

    def _on_window_destroy(self, window):
        """Window is destroyed... Quit the application.
        """
        AbstractWindow._on_window_destroy(self, window)
        del self.model
        del self.view

    def on_view_event(self, view, event):
        """Show a popup menu if button3 was pressed on the TreeView.
        """
        self._check_state(AbstractWindow.STATE_ACTIVE)

        # handle mouse button 3:
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self._construct_popup_menu(menu_def=self.ns_popup, event=event)

    def on_view_row_activated(self, view, path, column):
        """Double click on an element in the tree view.
        """
        self._check_state(AbstractWindow.STATE_ACTIVE)
        self.execute_action('OpenModelElement')

    def on_view_cursor_changed(self, view):
        """Another row is selected, execute a dummy action.
        """
        self.execute_action('SelectRow')

    def on_notebook_switch_page(self, notebook, tab, page_num):
        """Another page (tab) is put on the front of the diagram notebook.
        A dummy action is executed.
        """
        self.execute_action('TabChange')

#    def on_transient_window_closed(self, window):
#        assert window in self.__transient_windows
#        log.debug('%s closed.' % window)
#        self.__transient_windows.remove(window)

    def __on_transient_window_notify_title(self, window):
        pass

    #def __on_element_factory_signal(self, obj, key):
        #print '__on_element_factory_signal', key
        #factory = gaphor.resource(UML.ElementFactory)
        #self.set_capability('model', not factory.is_empty())

gtk.accel_map_add_filter('gaphor')
