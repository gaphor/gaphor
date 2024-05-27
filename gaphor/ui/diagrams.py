from __future__ import annotations

import logging

from generic.event import Event
from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.core import action, event_handler
from gaphor.core.modeling import (
    AttributeUpdated,
    Diagram,
    ModelFlushed,
    ModelReady,
    StyleSheet,
)
from gaphor.diagram.drop import drop
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor.event import ActionEnabled
from gaphor.i18n import translated_ui_string
from gaphor.transaction import Transaction
from gaphor.ui.abc import UIComponent
from gaphor.ui.diagrampage import DiagramPage, GtkView
from gaphor.ui.event import (
    CurrentDiagramChanged,
    DiagramClosed,
    ElementOpened,
)

log = logging.getLogger(__name__)


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", "diagrams.ui"))
    return builder


class Diagrams(UIComponent, ActionProvider):
    def __init__(
        self, event_manager, element_factory, properties, modeling_language, toolbox
    ):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self.modeling_language = modeling_language
        self.toolbox = toolbox
        self._notebook: Gtk.Widget = None
        self._page_handler_ids: list[int] = []

    def open(self):
        """Open the diagrams component."""
        builder = new_builder()
        self._notebook = builder.get_object("notebook")
        self._stack = builder.get_object("stack")
        self._page_handler_ids = [
            self._notebook.connect(
                "close-page",
                lambda _notebook, page: self.event_manager.handle(
                    DiagramClosed(page.get_child().diagram_page.get_diagram())
                ),
            ),
            self._notebook.connect("page-attached", self._on_page_changed),
            self._notebook.connect("page-detached", self._on_page_changed),
            self._notebook.connect("page-reordered", self._on_page_changed),
            self._notebook.connect(
                "notify::selected-page", self._on_current_page_changed
            ),
            self._notebook.connect_after("map", self._on_current_page_changed),
        ]

        self.event_manager.subscribe(self._on_show_diagram)
        self.event_manager.subscribe(self._on_show_element)
        self.event_manager.subscribe(self._on_close_diagram)
        self.event_manager.subscribe(self._on_name_change)
        self.event_manager.subscribe(self._on_flush_model)
        self.event_manager.subscribe(self._on_model_ready)

        self._on_model_ready()
        return self._stack

    def close(self):
        """Close the diagrams component."""
        self.event_manager.unsubscribe(self._on_model_ready)
        self.event_manager.unsubscribe(self._on_flush_model)
        self.event_manager.unsubscribe(self._on_name_change)
        self.event_manager.unsubscribe(self._on_close_diagram)
        self.event_manager.unsubscribe(self._on_show_element)
        self.event_manager.unsubscribe(self._on_show_diagram)
        if self._notebook:
            if parent := self._notebook.get_parent():
                parent.remove(self._notebook)
            self._notebook = None

    def get_current_diagram(self) -> Diagram | None:
        """Returns the current page of the notebook.

        Returns (DiagramPage): The current diagram page.
        """
        if not self._notebook:
            return None
        selected = self._notebook.get_selected_page()
        return selected.get_child().diagram_page.get_diagram() if selected else None

    def set_current_diagram(self, diagram: Diagram) -> bool:
        for page_num, widget in get_widgets_on_pages(self._notebook):
            if widget.diagram_page.get_diagram() is diagram:
                self._notebook.set_selected_page(self._notebook.get_nth_page(page_num))
                return True
        return False

    def get_current_view(self) -> GtkView:
        """Returns the current view of the diagram page.

        Returns (GtkView): The current view.
        """
        if not self._notebook:
            return None
        selected = self._notebook.get_selected_page()
        return selected and selected.get_child().diagram_page.get_view()

    def create_diagram_page(self, diagram: Diagram) -> DiagramPage:
        page = DiagramPage(
            diagram,
            self.event_manager,
            self.modeling_language,
        )
        widget = page.construct()
        widget.diagram_page = page

        apply_tool_select_controller(widget, self.toolbox)
        self._create_tab(diagram.name, widget)
        page.select_tool(self.toolbox.active_tool_name)
        self._update_action_state()
        return page

    def _create_tab(self, title, widget):
        """Creates a new Notebook tab with a label and close button.

        Args:
            title (str): The title of the tab, the diagram name.
            widget (Gtk.Widget): The child widget of the tab.
        """
        page = self._notebook.append(widget)
        page.set_title(title or "")
        self._notebook.set_selected_page(page)

        view = widget.diagram_page.view
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
                if page := notebook.get_nth_page(page_num):
                    page = page.get_child()
                    if diagram := page.diagram_page.get_diagram():
                        yield diagram.id

        self._stack.set_visible_child_name(
            "notebook" if notebook.get_n_pages() else "empty"
        )
        self.properties.set("opened-diagrams", list(diagram_ids()))

    def _on_current_page_changed(self, _notebook_or_tab_page=None, _gparam=None):
        diagram = self.get_current_diagram()
        self.event_manager.handle(CurrentDiagramChanged(diagram))
        self.properties.set("current-diagram", diagram.id if diagram else None)
        if view := self.get_current_view():
            view.grab_focus()

    @action(name="close-current-tab", shortcut="<Primary>w")
    def close_current_tab(self):
        diagram = self.get_current_diagram()
        self.event_manager.handle(DiagramClosed(diagram))

    @action(
        name="zoom-in",
        shortcut=("<Primary>equal", "<Primary>plus"),
    )
    def zoom_in(self):
        if view := self.get_current_view():
            view.zoom(1.2)

    @action(
        name="zoom-out",
        shortcut="<Primary>minus",
    )
    def zoom_out(self):
        if view := self.get_current_view():
            view.zoom(1 / 1.2)

    @action(
        name="zoom-100",
        shortcut="<Primary>0",
    )
    def zoom_100(self):
        if view := self.get_current_view():
            zx = view.matrix[0]
            view.zoom(1 / zx)

    @action(
        name="move-left-small",
        shortcut="<Alt>Left",
    )
    def move_left_small(self):
        self.translate_selected_elements(-1, 0)

    @action(
        name="move-left-large",
        shortcut="<Alt><Shift>Left",
    )
    def move_left_large(self):
        self.translate_selected_elements(-10, 0)

    @action(
        name="move-right-small",
        shortcut="<Alt>Right",
    )
    def move_right_small(self):
        self.translate_selected_elements(1, 0)

    @action(
        name="move-right-large",
        shortcut="<Alt><Shift>Right",
    )
    def move_right_large(self):
        self.translate_selected_elements(10, 0)

    @action(
        name="move-up-small",
        shortcut="<Alt>Up",
    )
    def move_up_small(self):
        self.translate_selected_elements(0, -1)

    @action(
        name="move-up-large",
        shortcut="<Alt><Shift>Up",
    )
    def move_up_large(self):
        self.translate_selected_elements(0, -10)

    @action(
        name="move-down-small",
        shortcut="<Alt>Down",
    )
    def move_down_small(self):
        self.translate_selected_elements(0, 1)

    @action(
        name="move-down-large",
        shortcut="<Alt><Shift>Down",
    )
    def move_down_large(self):
        self.translate_selected_elements(0, 10)

    def translate_selected_elements(self, dx: int, dy: int):
        view = self.get_current_view()
        diagram = self.get_current_diagram()
        if not (view and diagram):
            return

        selection = view.selection.selected_items

        with Transaction(self.event_manager):
            for item in selection:
                item.matrix.translate(dx, dy)

    @action(
        name="select-all",
        shortcut="<Primary>a",
    )
    def select_all(self):
        view = self.get_current_view()
        if view and view.has_focus():
            selection = view.selection
            selection.select_items(*view.model.get_all_items())
            self.event_manager.handle(
                DiagramSelectionChanged(
                    view, selection.focused_item, selection.selected_items
                )
            )

    @action(name="unselect-all", shortcut="<Primary><Shift>a")
    def unselect_all(self):
        view = self.get_current_view()
        if view and view.has_focus():
            selection = view.selection
            selection.unselect_all()
            self.event_manager.handle(
                DiagramSelectionChanged(
                    view, selection.focused_item, selection.selected_items
                )
            )

    @event_handler(ElementOpened)
    def _on_show_element(self, event: ElementOpened):
        view = self.get_current_view()
        diagram = self.get_current_diagram()
        if not (view and diagram):
            return
        x, y = view.matrix.inverse().transform_point(100, 100)
        with Transaction(self.event_manager):
            if item := drop(event.element, diagram, x, y):
                view.selection.unselect_all()
                view.selection.focused_item = item

    @event_handler(DiagramOpened)
    def _on_show_diagram(self, event: DiagramOpened):
        """Show a Diagram element in the Notebook.

        If a diagram is already open on a Notebook page, show that one,
        otherwise create a new Notebook page.

        Args:
            event: The service event that is calling the method.
        """
        diagram = event.diagram
        if not self.set_current_diagram(diagram):
            self.create_diagram_page(diagram)

    @event_handler(DiagramClosed)
    def _on_close_diagram(self, event: Event) -> None:
        """Callback to close the tab and remove the notebook page."""
        diagram = event.diagram

        for _page_num, widget in get_widgets_on_pages(self._notebook):
            if widget.diagram_page.get_diagram() is diagram:
                break
        else:
            return

        self._notebook.close_page(self._notebook.get_nth_page(_page_num))

        widget.diagram_page.close()
        self._update_action_state()

    @event_handler(ModelReady)
    def _on_model_ready(self, event=None):
        """Open the toplevel element and load toplevel diagrams."""
        if style_sheet := next(self.element_factory.select(StyleSheet), None):
            style_sheet.system_font_family = (
                Gtk.Settings.get_default().props.gtk_font_name.rsplit(" ", 1)[0]
            )

        diagram_ids = self.properties.get("opened-diagrams", [])
        current_diagram_id = self.properties.get("current-diagram", None)

        diagrams = [self.element_factory.lookup(id) for id in diagram_ids]
        if not any(diagrams):
            diagrams = self.element_factory.select(
                lambda e: e.isKindOf(Diagram) and not (e.owner and e.owner.owner)
            )
        for diagram in diagrams:
            if diagram:
                self.event_manager.handle(DiagramOpened(diagram))

        if current_diagram_id:
            current_diagram = self.element_factory.lookup(current_diagram_id)
            if self.set_current_diagram(current_diagram):
                return
        if self._notebook and self._notebook.get_n_pages():
            self._notebook.set_selected_page(self._notebook.get_nth_page(0))

    @event_handler(ModelFlushed)
    def _on_flush_model(self, event):
        """Close all tabs."""
        for page in self._notebook.get_pages():
            if page:
                self._notebook.close_page(page)
        self._update_action_state()

    def _update_action_state(self):
        enabled = self._notebook and self._notebook.get_n_pages() > 0

        for action_name in ("win.zoom-in", "win.zoom-out", "win.zoom-100"):
            self.event_manager.handle(ActionEnabled(action_name, enabled))

    @event_handler(AttributeUpdated)
    def _on_name_change(self, event):
        if event.property is not Diagram.name:
            return
        for page in range(self._notebook.get_n_pages()):
            widget = self._notebook.get_nth_page(page)
            if event.element is widget.get_child().diagram_page.diagram:
                widget.set_title(event.new_value or "")
                if widget is self._notebook.get_selected_page():
                    self.event_manager.handle(CurrentDiagramChanged(event.element))
                return


def apply_tool_select_controller(widget, toolbox):
    ctrl = Gtk.EventControllerKey.new()
    widget.add_controller(ctrl)

    def on_shortcut(_ctrl, keyval, _keycode, state):
        toolbox.activate_shortcut(keyval, state)

    ctrl.connect("key-pressed", on_shortcut)


def get_widgets_on_pages(notebook):
    """Gets the widget on each open page Notebook page.

    The page is the page number in the Notebook (0 indexed) and the widget
    is the child widget on each page.

    Returns:
        List of tuples (page, widget) of the currently open Notebook pages.
    """
    if not notebook:
        return

    for page_num in range(notebook.get_n_pages()):
        yield (page_num, notebook.get_nth_page(page_num).get_child())
