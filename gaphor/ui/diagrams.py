import logging
from typing import List, Tuple

from generic.event import Event
from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.core import action, event_handler
from gaphor.core.modeling import AttributeUpdated, Diagram, ModelFlushed
from gaphor.event import ActionEnabled
from gaphor.ui.abc import UIComponent
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.event import DiagramClosed, DiagramOpened, DiagramSelectionChanged

log = logging.getLogger(__name__)


class Diagrams(UIComponent, ActionProvider):
    def __init__(
        self, event_manager, element_factory, properties, modeling_language, toolbox
    ):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self.modeling_language = modeling_language
        self.toolbox = toolbox
        self._notebook: Gtk.Notebook = None
        self._page_handler_ids: List[int] = []

    def open(self):
        """Open the diagrams component.

        Returns:
            The Gtk.Notebook.
        """

        self._notebook = Gtk.Notebook()
        self._notebook.props.scrollable = True
        self._notebook.show()

        self._notebook.connect("destroy", self._on_notebook_destroy)
        self._notebook.connect("switch-page", self._on_switch_page)
        self._page_handler_ids = [
            self._notebook.connect("page-added", self._on_page_changed),
            self._notebook.connect("page-removed", self._on_page_changed),
            self._notebook.connect("page-reordered", self._on_page_changed),
        ]

        self.event_manager.subscribe(self._on_show_diagram)
        self.event_manager.subscribe(self._on_close_diagram)
        self.event_manager.subscribe(self._on_name_change)
        self.event_manager.subscribe(self._on_flush_model)

        return self._notebook

    def close(self):
        """Close the diagrams component."""

        self.event_manager.unsubscribe(self._on_flush_model)
        self.event_manager.unsubscribe(self._on_name_change)
        self.event_manager.unsubscribe(self._on_close_diagram)
        self.event_manager.unsubscribe(self._on_show_diagram)
        if self._notebook:
            if Gtk.get_major_version() == 3:
                self._notebook.destroy()
            else:
                parent = self._notebook.get_parent()
                if parent:
                    parent.remove(self._notebook)
            self._notebook = None

    def get_current_diagram(self):
        """Returns the current page of the notebook.

        Returns (DiagramPage): The current diagram page.
        """

        if not self._notebook:
            return None
        page_num = self._notebook.get_current_page()
        child_widget = self._notebook.get_nth_page(page_num)
        return child_widget and child_widget.diagram_page.get_diagram()

    def get_current_view(self):
        """Returns the current view of the diagram page.

        Returns (GtkView): The current view.
        """
        if not self._notebook:
            return None
        page_num = self._notebook.get_current_page()
        child_widget = self._notebook.get_nth_page(page_num)
        return child_widget and child_widget.diagram_page.get_view()

    def create_tab(self, title, widget):
        """Creates a new Notebook tab with a label and close button.

        Args:
            title (str): The title of the tab, the diagram name.
            widget (Gtk.Widget): The child widget of the tab.
        """

        page_num = self._notebook.append_page(
            child=widget, tab_label=tab_label(title, widget, self.event_manager)
        )
        self._notebook.set_current_page(page_num)
        self._notebook.set_tab_reorderable(widget, True)

        view = widget.diagram_page.view
        self.event_manager.handle(
            DiagramSelectionChanged(
                view, view.selection.focused_item, view.selection.selected_items
            )
        )

    def _on_notebook_destroy(self, notebook):
        for id in self._page_handler_ids:
            notebook.disconnect(id)

    def _on_switch_page(self, notebook, page, new_page_num):
        view = page.diagram_page.view
        self.event_manager.handle(
            DiagramSelectionChanged(
                view, view.selection.focused_item, view.selection.selected_items
            )
        )

    def _on_page_changed(self, notebook, _page, _page_num):
        def diagram_ids():
            notebook = self._notebook
            if not notebook:
                return
            for page_num in range(notebook.get_n_pages()):
                page = notebook.get_nth_page(page_num)
                if page:
                    diagram = page.diagram_page.get_diagram()
                    if diagram:
                        yield diagram.id

        self.properties.set("opened-diagrams", list(diagram_ids()))
        log.debug(f"pages changed: {self.properties.get('opened-diagrams')}")

    @action(name="close-current-tab", shortcut="<Primary>w")
    def close_current_tab(self):
        diagram = self.get_current_diagram()
        self.event_manager.handle(DiagramClosed(diagram))

    @action(
        name="zoom-in",
        shortcut="<Primary>equal",
    )
    def zoom_in(self):
        view = self.get_current_view()
        if view:
            view.zoom(1.2)

    @action(
        name="zoom-out",
        shortcut="<Primary>minus",
    )
    def zoom_out(self):
        view = self.get_current_view()
        if view:
            view.zoom(1 / 1.2)

    @action(
        name="zoom-100",
        shortcut="<Primary>0",
    )
    def zoom_100(self):
        view = self.get_current_view()
        if view:
            zx = view.matrix[0]
            view.zoom(1 / zx)

    @action(
        name="select-all",
        shortcut="<Primary>a",
    )
    def select_all(self):
        view = self.get_current_view()
        if view and view.has_focus():
            view.selection.select_items(*view.model.get_all_items())

    @action(name="unselect-all", shortcut="<Primary><Shift>a")
    def unselect_all(self):
        view = self.get_current_view()
        if view and view.has_focus():
            view.selection.unselect_all()

    @event_handler(DiagramOpened)
    def _on_show_diagram(self, event):
        """Show a Diagram element in the Notebook.

        If a diagram is already open on a Notebook page, show that one,
        otherwise create a new Notebook page.

        Args:
            event: The service event that is calling the method.
        """

        diagram = event.diagram

        # Try to find an existing diagram page and give it focus
        for page, widget in get_widgets_on_pages(self._notebook):
            if widget.diagram_page.get_diagram() is diagram:
                self._notebook.set_current_page(page)
                self.get_current_view().grab_focus()
                return widget.diagram_page

        # No existing diagram page found, creating one
        page = DiagramPage(
            diagram,
            self.event_manager,
            self.element_factory,
            self.properties,
            self.modeling_language,
        )
        widget = page.construct()
        widget.diagram_page = page

        apply_tool_select_controller(widget, self.toolbox)
        self.create_tab(diagram.name, widget)
        page.select_tool(self.toolbox.active_tool_name)
        self.get_current_view().grab_focus()
        self._update_action_state()
        return page

    @event_handler(DiagramClosed)
    def _on_close_diagram(self, event: Event) -> None:
        """Callback to close the tab and remove the notebook page."""

        diagram = event.diagram

        for page_num, widget in get_widgets_on_pages(self._notebook):
            if widget.diagram_page.get_diagram() is diagram:
                break
        else:
            log.warn(f"No tab found for diagram {diagram}")
            return

        self._notebook.remove_page(page_num)
        widget.diagram_page.close()
        if Gtk.get_major_version() == 3:
            widget.destroy()
        self._update_action_state()

    @event_handler(ModelFlushed)
    def _on_flush_model(self, event):
        """Close all tabs."""
        while self._notebook.get_n_pages():
            self._notebook.remove_page(0)
        self._update_action_state()

    def _update_action_state(self):
        enabled = self._notebook and self._notebook.get_n_pages() > 0

        for action_name in ["win.zoom-in", "win.zoom-out", "win.zoom-100"]:
            self.event_manager.handle(ActionEnabled(action_name, enabled))

    @event_handler(AttributeUpdated)
    def _on_name_change(self, event):
        if event.property is Diagram.name:
            for page in range(self._notebook.get_n_pages()):
                widget = self._notebook.get_nth_page(page)
                if event.element is widget.diagram_page.diagram:
                    self._notebook.set_tab_label(
                        widget, tab_label(event.new_value, widget, self.event_manager)
                    )


def apply_tool_select_controller(widget, toolbox):
    if Gtk.get_major_version() == 3:
        ctrl = Gtk.EventControllerKey.new(widget)
        widget._toolbox_controller = ctrl
    else:
        ctrl = Gtk.EventControllerKey.new()
        widget.add_controller(ctrl)

    def on_shortcut(_ctrl, keyval, _keycode, state):
        toolbox.activate_shortcut(keyval, state)

    ctrl.connect("key-pressed", on_shortcut)


def tab_label(title, widget, event_manager):
    tab_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    button = Gtk.Button()
    button.get_style_context().add_class("flat")
    button.set_focus_on_click(False)

    button.connect(
        "clicked",
        lambda _button: event_manager.handle(
            DiagramClosed(widget.diagram_page.get_diagram())
        ),
    )

    label = Gtk.Label.new(title)
    if Gtk.get_major_version() == 3:
        tab_box.pack_start(child=label, expand=True, fill=True, padding=0)
        close_image = Gtk.Image.new_from_icon_name(
            icon_name="window-close", size=Gtk.IconSize.BUTTON
        )
        button.add(close_image)
        tab_box.pack_start(child=button, expand=False, fill=False, padding=0)
        tab_box.show_all()
    else:
        tab_box.append(label)
        close_image = Gtk.Image.new_from_icon_name("window-close")
        button.set_child(close_image)
        tab_box.append(button)
        tab_box.show()

    return tab_box


def get_widgets_on_pages(notebook):
    """Gets the widget on each open page Notebook page.

    The page is the page number in the Notebook (0 indexed) and the widget
    is the child widget on each page.

    Returns:
        List of tuples (page, widget) of the currently open Notebook pages.
    """

    widgets_on_pages: List[Tuple[int, Gtk.Widget]] = []
    if not notebook:
        return widgets_on_pages

    num_pages = notebook.get_n_pages()
    for page_num in range(num_pages):
        widget = notebook.get_nth_page(page_num)
        widgets_on_pages.append((page_num, widget))
    return widgets_on_pages
