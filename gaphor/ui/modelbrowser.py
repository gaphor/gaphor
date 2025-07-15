from __future__ import annotations

from gi.repository import Gdk, Gio, GLib, GObject, Gtk

from gaphor.abc import ActionProvider, TreeItem, TreeModel
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.core.modeling import Base, Diagram
from gaphor.diagram.deletable import deletable
from gaphor.diagram.event import DiagramOpened, DiagramSelectionChanged
from gaphor.diagram.group import Root, RootType, change_owner, owner
from gaphor.diagram.tools.dnd import ElementDragData
from gaphor.event import Notification
from gaphor.i18n import gettext
from gaphor.services.modelinglanguage import ModelingLanguageChanged
from gaphor.transaction import Transaction
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import apply_action_group
from gaphor.ui.event import (
    ElementFocused,
    ElementOpened,
    ModelSelectionChanged,
)
from gaphor.ui.treesearch import search, sorted_tree_walker

START_EDIT_DELAY = 100  # ms


class ModelBrowser(UIComponent, ActionProvider):
    def __init__(
        self, event_manager, component_registry, element_factory, modeling_language
    ):
        self.event_manager = event_manager
        self.component_registry = component_registry
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.model: TreeModel | None = None
        self.search_bar = None
        self._selection_changed_id = 0
        self.sorter = None
        self.selection = None
        self.tree_view = None
        self.top_level = None

    def open(self):
        self.event_manager.subscribe(self.on_diagram_selection_changed)
        self.event_manager.subscribe(self.on_modeling_language_changed)

        model_type = self.modeling_language.model_browser_model
        model = self.component_registry.partial(model_type)(
            on_select=self._on_select, on_sync=self._on_sync
        )
        self.model = model

        tree_model = Gtk.TreeListModel.new(
            model.root,
            passthrough=False,
            autoexpand=False,
            create_func=model.child_model,
        )

        def tree_item_sort(a, b, *user_data):
            return model.tree_item_sort(a, b)

        self.sorter = Gtk.CustomSorter.new(tree_item_sort)
        tree_sorter = Gtk.TreeListRowSorter.new(self.sorter)
        sort_model = Gtk.SortListModel.new(tree_model, tree_sorter)
        self.selection = Gtk.MultiSelection.new(sort_model)

        factory = Gtk.SignalListItemFactory.new()
        factory.connect(
            "setup",
            list_item_factory_setup,
            self.selection,
            self.event_manager,
            self.modeling_language,
            model.template,
        )
        self.tree_view = Gtk.ListView.new(self.selection, factory)
        self.tree_view.set_vexpand(True)

        def selection_changed(selection, _position, _n_items):
            if element := get_first_selected_item(selection).get_item().element:
                self.event_manager.handle(ModelSelectionChanged(self, element))

        self._selection_changed_id = self.selection.connect(
            "selection-changed", selection_changed
        )

        def list_view_activate(list_view, position):
            if element := self.selection.get_item(position).get_item().element:  # type: ignore[union-attr]
                self.focus_element(element)

        self.tree_view.connect("activate", list_view_activate)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.tree_view)

        apply_action_group(self, "selection", self.tree_view)

        self.tree_view.add_controller(
            create_popup_controller(
                self.tree_view, self.selection, self.modeling_language
            )
        )

        self.search_bar = create_search_bar(SearchEngine(self.model, self.tree_view))

        self.search_bar.set_key_capture_widget(self.tree_view)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.append(self.search_bar)
        box.append(scrolled_window)
        self.top_level = box

        return box

    def close(self):
        self.event_manager.unsubscribe(self.on_diagram_selection_changed)
        self.event_manager.unsubscribe(self.on_modeling_language_changed)
        if self.model:
            self.model.shutdown()
        self.model = None
        self.search_bar = None
        self._selection_changed_id = 0
        self.sorter = None
        self.selection = None
        self.tree_view = None
        self.top_level = None

    def select_element(self, element: Base) -> int | None:
        assert self.model
        return select_element(self.model, self.tree_view, element)

    def select_element_quietly(self, element):
        """Select element, but do not trigger a ModelSelectionChanged event."""
        if not self.selection:
            return

        self.selection.handler_block(self._selection_changed_id)
        try:
            self.select_element(element)
        finally:
            self.selection.handler_unblock(self._selection_changed_id)

    def get_selected_elements(self) -> list[Base]:
        assert self.model
        return get_selected_elements(self.selection)

    def get_selected_element(self) -> Base | None:
        assert self.model
        return next(iter(self.get_selected_elements()), None)

    def focus_element(self, element):
        assert element
        if isinstance(element, Diagram):
            self.event_manager.handle(DiagramOpened(element))
        else:
            self.event_manager.handle(ElementFocused(element))

    def open_element(self, element):
        assert element
        if isinstance(element, Diagram):
            self.event_manager.handle(DiagramOpened(element))
        else:
            self.event_manager.handle(ElementOpened(element))

    def _on_select(self, element):
        self.select_element_quietly(element)

    def _on_sync(self):
        if self.sorter:
            self.sorter.changed(Gtk.SorterChange.DIFFERENT)

    @action(name="selection.open")
    def tree_view_open_selected(self):
        element = self.get_selected_element()
        if element:
            self.open_element(element)

    @action(name="selection.show-in-diagram")
    def tree_view_show_in_diagram(self, diagram_id: str) -> None:
        element = self.element_factory.lookup(diagram_id)
        self.event_manager.handle(DiagramOpened(element))

    @action(name="selection.rename", shortcut="F2")
    def tree_view_rename_selected(self):
        if row_item := get_first_selected_item(self.selection):
            tree_item = row_item.get_item()
            GLib.timeout_add(START_EDIT_DELAY, tree_item.start_editing)

    @action(name="win.create-diagram")
    def tree_view_create_diagram(self, diagram_kind: str):
        element: Base | RootType | None = self.get_selected_element()

        with Transaction(self.event_manager):
            diagram_type = next(
                dt
                for dt in self.modeling_language.diagram_types
                if dt.id == diagram_kind
            )
            try:
                diagram = diagram_type.create(
                    self.element_factory, None if element is Root else element
                )
                diagram.name = diagram.gettext("New Diagram")
            except TypeError as e:
                self.event_manager.handle(Notification(str(e)))
                return
        self.select_element(diagram)
        self.event_manager.handle(DiagramOpened(diagram))
        self.tree_view_rename_selected()

    def element_type(self, id: str):
        return next(
            el_type
            for el_type in self.modeling_language.element_types
            if el_type.id == id
        )

    @action(name="win.create-element")
    def tree_view_create_element(self, id: str):
        own = self.get_selected_element()
        element_def = self.element_type(id)

        with Transaction(self.event_manager):
            element = self.element_factory.create(element_def.element_type)
            element.name = element_def.name
            if own:
                change_owner(own, element)

            self.select_element(element)
            self.tree_view_rename_selected()

    @action(name="selection.delete", shortcut="Delete")
    def tree_view_delete(self):
        with Transaction(self.event_manager):
            for element in self.get_selected_elements():
                if deletable(element):
                    element.unlink()

    @action(name="win.search", shortcut="<Primary>f")
    def tree_view_search(self):
        if self.search_bar:
            self.search_bar.set_search_mode(True)

    @action(name="win.show-in-model-browser")
    def show_in_model_browser(self, id: str):
        if element := self.element_factory.lookup(id):
            self.select_element(element)

    @event_handler(DiagramSelectionChanged)
    def on_diagram_selection_changed(self, event):
        if not event.focused_item:
            return
        if element := event.focused_item.subject:
            self.select_element_quietly(element)

    @event_handler(ModelingLanguageChanged)
    def on_modeling_language_changed(self, event: ModelingLanguageChanged) -> None:
        """Reconfigures the model browser based on the modeling language selected."""
        if (not self.top_level) or type(
            self.model
        ) is self.modeling_language.model_browser_model:
            return

        bin = self.top_level.get_parent()
        self.close()
        widget = self.open()
        if bin:
            bin.set_child(widget)


class SearchEngine:
    def __init__(self, model, tree_view):
        self.model = model
        self.tree_view = tree_view
        self.selection = self.tree_view.get_model()

    def text_changed(self, search_text):
        selected_item = get_first_selected_item(self.selection)
        if next_item := search(
            search_text,
            sorted_tree_walker(
                self.model,
                start_tree_item=selected_item and selected_item.get_item(),
                from_current=True,
            ),
        ):
            select_element(self.model, self.tree_view, next_item.element)

    def search_next(self, search_text):
        selected_item = get_first_selected_item(self.selection)
        if next_item := search(
            search_text,
            sorted_tree_walker(
                self.model,
                start_tree_item=selected_item and selected_item.get_item(),
                from_current=False,
            ),
        ):
            select_element(self.model, self.tree_view, next_item.element)


def get_selected_elements(selection: Gtk.SelectionModel) -> list[Base]:
    bitset = selection.get_selection()
    return [
        e
        for n in range(bitset.get_size())
        if (e := selection.get_item(bitset.get_nth(n)).get_item().element)
    ]


def get_first_selected_item(selection):
    bitset = selection.get_selection()
    pos = bitset.get_nth(0)
    return selection.get_item(pos)


def select_element(
    model: TreeModel, tree_view: Gtk.ListView, element: Base, unselect_rest=True
) -> int | None:
    def expand_up_to_element(element, expand=False) -> int | None:
        if element in (Root, None):
            return 0
        if (n := expand_up_to_element(owner(element), expand=True)) is None:
            return None
        while row := selection.get_item(n):
            item: TreeItem = row.get_item()
            if model.should_expand(item, element):
                row.set_expanded(True)
            elif item.element is element:
                if expand:
                    row.set_expanded(True)
                return n
            n += 1
        return None

    selection = tree_view.get_model()
    pos = expand_up_to_element(element)
    if pos is not None:
        selection.select_item(pos, unselect_rest)
        tree_view.activate_action("list.scroll-to-item", GLib.Variant.new_uint32(pos))
    return pos


def create_search_bar(search_engine: SearchEngine):
    def on_search_changed(entry):
        search_engine.text_changed(entry.get_text())

    def on_search_next(entry):
        search_engine.search_next(entry.get_text())

    search_entry = Gtk.SearchEntry.new()
    search_entry.connect("search-changed", on_search_changed)
    search_entry.connect("activate", on_search_next)
    search_entry.connect("next-match", on_search_next)
    search_bar = Gtk.SearchBar.new()
    search_bar.set_child(search_entry)
    search_bar.connect_entry(search_entry)
    search_bar.set_show_close_button(True)

    return search_bar


def create_popup_controller(tree_view, selection, modeling_language):
    menus: dict[str, Gtk.PopoverMenu] = {}

    def on_show_popup(ctrl, n_press, x, y):
        if not ctrl.get_last_event().triggers_context_menu():
            return

        selection.unselect_all()
        language_name = modeling_language.active_modeling_language
        menu = menus.get(language_name)
        if not menu:
            menu = Gtk.PopoverMenu.new_from_model(
                toplevel_popup_model(modeling_language)
            )
            menu.set_parent(tree_view)
            menu.set_has_arrow(False)
            menus[language_name] = menu

        gdk_rect = Gdk.Rectangle()
        gdk_rect.x = x
        gdk_rect.y = y
        gdk_rect.width = gdk_rect.height = 1

        menu.set_pointing_to(gdk_rect)
        menu.popup()

    ctrl = Gtk.GestureClick.new()
    ctrl.set_button(0)
    ctrl.connect("pressed", on_show_popup)
    return ctrl


def toplevel_popup_model(modeling_language) -> Gio.Menu:
    model = create_diagram_types_model(modeling_language)

    part = Gio.Menu.new()
    menu_item = Gio.MenuItem.new(gettext("Package"), "win.create-element")
    menu_item.set_attribute_value("target", GLib.Variant.new_string("package"))
    part.append_item(menu_item)
    model.prepend_section(None, part)
    return model


def list_item_factory_setup(
    _factory, list_item, selection, event_manager, modeling_language, template
):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        template,
        -1,
    )
    row = builder.get_object("row")
    row.menu = None

    def on_show_popup(ctrl, n_press, x, y):
        if not ctrl.get_last_event().triggers_context_menu():
            return

        list_item.get_child().activate_action(
            "list.select-item",
            GLib.Variant.new_tuple(
                GLib.Variant.new_uint32(list_item.get_position()),
                GLib.Variant.new_boolean(False),
                GLib.Variant.new_boolean(False),
            ),
        )
        element = list_item.get_item().get_item().element
        if not element:
            return

        if not row.menu:
            row.menu = Gtk.PopoverMenu.new_from_model(
                popup_model(element, modeling_language)
            )
            row.menu.set_parent(row)
        else:
            row.menu.set_menu_model(popup_model(element, modeling_language))
        row.menu.popup()

    ctrl = Gtk.GestureClick.new()
    ctrl.set_button(0)
    ctrl.connect("pressed", on_show_popup)
    row.add_controller(ctrl)

    drag_source = Gtk.DragSource.new()
    drag_source.set_actions(Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
    drag_source.connect("prepare", list_item_drag_prepare, list_item, selection)
    drag_source.connect("drag-begin", list_item_drag_begin, list_item)
    row.add_controller(drag_source)

    drop_target = Gtk.DropTarget.new(ElementDragData.__gtype__, Gdk.DragAction.COPY)
    drop_target.set_preload(True)
    drop_target.connect("accept", list_item_drop_accept, list_item)
    drop_target.connect("motion", list_item_drop_motion, list_item)
    drop_target.connect("leave", list_item_drop_leave, list_item)
    drop_target.connect("drop", list_item_drop_drop, list_item, event_manager)
    row.add_controller(drop_target)

    def done_editing(text_field, should_commit):
        list_item.get_item().get_item().editing = False
        if should_commit:
            tree_item = list_item.get_item().get_item()
            with Transaction(event_manager):
                tree_item.editable_text = text_field.editable_text

    builder.get_object("text").connect("done-editing", done_editing)


def list_item_drag_prepare(
    source: Gtk.DragSource,
    x: int,
    y: int,
    list_item: Gtk.ListItem,
    selection: Gtk.SelectionModel,
) -> Gdk.ContentProvider | None:
    elements = get_selected_elements(selection)
    under_cursor = list_item.get_item().get_item().element

    if not elements or under_cursor not in elements:
        elements = [under_cursor]

    v = GObject.Value(ElementDragData.__gtype__, ElementDragData(elements=elements))
    return Gdk.ContentProvider.new_for_value(v)


def list_item_drag_begin(
    source: Gtk.DragSource,
    drag: Gdk.Drag,
    list_item: Gtk.ListItem,
) -> None:
    tree_item = list_item.get_item().get_item()
    display = Gdk.Display.get_default()
    theme_icon = Gtk.IconTheme.get_for_display(display).lookup_icon(
        tree_item.icon,
        None,
        24,
        1,
        Gtk.TextDirection.NONE,
        Gtk.IconLookupFlags.FORCE_SYMBOLIC,
    )
    source.set_icon(theme_icon, 0, 0)


def list_item_drop_accept(
    target: Gtk.DropTarget, drop: Gdk.Drop, list_item: Gtk.ListItem
) -> bool:
    return drop.get_formats().contain_gtype(ElementDragData.__gtype__)  # type: ignore[no-any-return]
    # Should check if grouping is possible: return dest_element is None or can_group(dest_element, element)


def list_item_drop_motion(
    target: Gtk.DropTarget, x: int, y: int, list_item: Gtk.ListItem
) -> Gdk.DragAction:
    widget = target.get_widget()
    if y < 4:
        widget.add_css_class("move-element-above")
    else:
        widget.remove_css_class("move-element-above")

    return Gdk.DragAction.COPY


def list_item_drop_leave(
    target: Gtk.DropTarget, list_item: Gtk.ListItem
) -> Gdk.DragAction:
    widget = target.get_widget()
    widget.remove_css_class("move-element-above")


def list_item_drop_drop(
    target: Gtk.DropTarget,
    value: ElementDragData,
    x: int,
    y: int,
    list_item: Gtk.ListItem,
    event_manager,
) -> Gdk.DragAction:
    list_item_drop_leave(target, list_item)

    tree_item = list_item.get_item().get_item()
    dest_element = tree_item.element
    if y < 4:
        dest_element = owner(dest_element)
        if dest_element is Root:
            dest_element = None

    with Transaction(event_manager) as tx:
        # This view is concerned with owner relationships.
        # Let's check if the owner relation has actually changed,
        # Otherwise roll back, to not confuse the user.
        for element in value.elements:
            if not change_owner(dest_element, element):
                tx.rollback()
                return False

    return True


def popup_model(element, modeling_language):
    model = Gio.Menu.new()

    part = Gio.Menu.new()

    part.append(
        gettext("_Open") if isinstance(element, Diagram) else gettext("Add to diagram"),
        "selection.open",
    )
    part.append(gettext("_Rename"), "selection.rename")
    model.append_section(None, part)

    part = Gio.Menu.new()
    diagram_submenu = create_diagram_types_model(modeling_language, element)
    if diagram_submenu.get_n_items():
        part.append_submenu(gettext("New _Diagram"), diagram_submenu)

    if any(
        isinstance(element, element_type.allowed_owning_elements)
        for element_type in modeling_language.element_types
    ):
        part.append_submenu(
            gettext("New _Element"),
            create_element_types_model(modeling_language, element),
        )
    model.append_section(None, part)

    part = Gio.Menu.new()
    part.append(gettext("De_lete"), "selection.delete")
    model.append_section(None, part)

    if not element:
        return model

    part = Gio.Menu.new()
    for presentation in element.presentation:
        if diagram := presentation.diagram:
            menu_item = Gio.MenuItem.new(
                gettext("Show in “{diagram}”").format(diagram=diagram.name),
                "selection.show-in-diagram",
            )
            menu_item.set_attribute_value("target", GLib.Variant.new_string(diagram.id))
            part.append_item(menu_item)

        # Play it safe with an (arbitrary) upper bound
        if part.get_n_items() > 29:
            break

    if part.get_n_items() > 0:
        model.append_section(None, part)
    return model


def create_diagram_types_model(modeling_language, element=None):
    model = Gio.Menu.new()

    part = Gio.Menu.new()
    for diagram_type in modeling_language.diagram_types:
        if diagram_type.allowed(element):
            menu_item = Gio.MenuItem.new(
                gettext(diagram_type.name), "win.create-diagram"
            )
            menu_item.set_attribute_value(
                "target", GLib.Variant.new_string(diagram_type.id)
            )
            part.append_item(menu_item)

    if part.get_n_items():
        model.append_section(None, part)

    return model


def create_element_types_model(modeling_language, element):
    model = Gio.Menu.new()

    for id, name, _, allowed_owning_elements in modeling_language.element_types:
        if isinstance(element, allowed_owning_elements):
            menu_item = Gio.MenuItem.new(gettext(name), "win.create-element")
            menu_item.set_attribute_value("target", GLib.Variant.new_string(id))
            model.append_item(menu_item)

    return model
