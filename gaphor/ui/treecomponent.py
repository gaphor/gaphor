from __future__ import annotations

import sys

from gi.repository import Gdk, GLib, GObject, Gtk

from gaphor import UML
from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.core.modeling import (
    DerivedSet,
    Diagram,
    Element,
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
)
from gaphor.core.modeling.event import AttributeUpdated, DerivedAdded, DerivedDeleted
from gaphor.diagram.tools.dnd import ElementDragData
from gaphor.i18n import gettext, translated_ui_string
from gaphor.transaction import Transaction
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import create_action_group
from gaphor.ui.event import DiagramOpened, DiagramSelectionChanged, ElementOpened
from gaphor.ui.namespace import diagram_name_for_type, popup_model
from gaphor.ui.namespacemodel import change_owner
from gaphor.ui.treemodel import (
    RelationshipItem,
    TreeItem,
    TreeModel,
    tree_item_sort,
    visible,
)
from gaphor.ui.treesearch import search, sorted_tree_walker

START_EDIT_DELAY = 100  # ms


class TreeComponent(UIComponent, ActionProvider):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.model = TreeModel()
        self.search_bar = None

    def open(self):
        self.event_manager.subscribe(self.on_element_created)
        self.event_manager.subscribe(self.on_element_deleted)
        self.event_manager.subscribe(self.on_owner_changed)
        self.event_manager.subscribe(self.on_owned_element_changed)
        self.event_manager.subscribe(self.on_attribute_changed)
        self.event_manager.subscribe(self.on_model_ready)
        self.event_manager.subscribe(self.on_diagram_selection_changed)

        tree_model = Gtk.TreeListModel.new(
            self.model.root,
            passthrough=False,
            autoexpand=False,
            create_func=self.model.child_model,
            user_data=None,
        )

        self.sorter = Gtk.CustomSorter.new(tree_item_sort)
        tree_sorter = Gtk.TreeListRowSorter.new(self.sorter)
        sort_model = Gtk.SortListModel.new(tree_model, tree_sorter)
        self.selection = Gtk.SingleSelection.new(sort_model)

        factory = Gtk.SignalListItemFactory.new()
        factory.connect(
            "setup", list_item_factory_setup, self.event_manager, self.modeling_language
        )
        self.tree_view = Gtk.ListView.new(self.selection, factory)
        self.tree_view.set_vexpand(True)

        def list_view_activate(list_view, position):
            list_view.activate_action("tree-view.open", None)

        self.tree_view.connect("activate", list_view_activate)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.tree_view)

        action_group, shortcuts = create_action_group(self, "tree-view")
        scrolled_window.insert_action_group("tree-view", action_group)
        self.tree_view.add_controller(create_popup_controller(shortcuts))

        self.search_bar = create_search_bar(SearchEngine(self.model, self.tree_view))

        self.search_bar.set_key_capture_widget(self.tree_view)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.append(self.search_bar)
        box.append(scrolled_window)

        self.on_model_ready()

        return box

    def close(self):
        self.event_manager.unsubscribe(self.on_element_created)
        self.event_manager.unsubscribe(self.on_element_deleted)
        self.event_manager.unsubscribe(self.on_owner_changed)
        self.event_manager.unsubscribe(self.on_owned_element_changed)
        self.event_manager.unsubscribe(self.on_attribute_changed)
        self.event_manager.unsubscribe(self.on_model_ready)
        self.event_manager.unsubscribe(self.on_diagram_selection_changed)

    def select_element(self, element: Element) -> int | None:
        return select_element(self.tree_view, element)

    def get_selected_element(self) -> Element | None:
        assert self.model
        if tree_item := self.selection.get_selected_item():
            return tree_item.get_item().element  # type: ignore[no-any-return]
        return None

    @action(name="tree-view.open")
    def tree_view_open_selected(self):
        element = self.get_selected_element()
        if isinstance(element, Diagram):
            self.event_manager.handle(DiagramOpened(element))
        else:
            self.event_manager.handle(ElementOpened(element))

    @action(name="tree-view.show-in-diagram")
    def tree_view_show_in_diagram(self, diagram_id: str) -> None:
        element = self.element_factory.lookup(diagram_id)
        self.event_manager.handle(DiagramOpened(element))

    @action(name="tree-view.rename", shortcut="F2")
    def tree_view_rename_selected(self):
        if row_item := self.selection.get_selected_item():
            tree_item: TreeItem = row_item.get_item()
            GLib.timeout_add(START_EDIT_DELAY, tree_item.start_editing)

    @action(name="win.create-diagram")
    def tree_view_create_diagram(self, diagram_type: str):
        element = self.get_selected_element()
        while element and not isinstance(element, UML.NamedElement):
            element = element.owner

        with Transaction(self.event_manager):
            diagram = self.element_factory.create(Diagram)
            if isinstance(element, UML.NamedElement):
                diagram.element = element
            diagram.name = diagram_name_for_type(self.modeling_language, diagram_type)
            diagram.diagramType = diagram_type
        self.select_element(diagram)
        self.event_manager.handle(DiagramOpened(diagram))
        self.tree_view_rename_selected()

    @action(name="tree-view.create-package")
    def tree_view_create_package(self):
        element = self.get_selected_element()
        assert isinstance(element, UML.Package)
        with Transaction(self.event_manager):
            package = self.element_factory.create(UML.Package)
            package.package = element
            package.name = (
                gettext("{name} package").format(name=element.name)
                if element
                else gettext("New model")
            )
        self.select_element(package)
        self.tree_view_rename_selected()

    @action(name="tree-view.delete")
    def tree_view_delete(self):
        if element := self.get_selected_element():
            with Transaction(self.event_manager):
                element.unlink()

    @action(name="win.search", shortcut="<Primary>f")
    def tree_view_search(self):
        if self.search_bar:
            self.search_bar.set_search_mode(True)

    @event_handler(ElementCreated)
    def on_element_created(self, event: ElementCreated):
        self.model.add_element(event.element)

    @event_handler(ElementDeleted)
    def on_element_deleted(self, event: ElementDeleted):
        self.model.remove_element(event.element)

    @event_handler(DerivedAdded, DerivedDeleted)
    def on_owned_element_changed(self, event):
        """Ensure we update the node once owned elements change."""
        if event.property is Element.ownedElement:
            self.model.notify_child_model(event.element)

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        # Should check on ownedElement as well, since it may not have been updated
        # before this thing triggers
        if (event.property is not Element.owner) or not visible(event.element):
            return
        element = event.element
        self.model.remove_element(element, former_owner=event.old_value)
        self.model.add_element(element)
        self.select_element(element)

    @event_handler(AttributeUpdated)
    def on_attribute_changed(self, event: AttributeUpdated):
        self.model.sync(event.element)
        self.sorter.changed(Gtk.SorterChange.DIFFERENT)

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, event=None):
        model = self.model
        model.clear()

        for element in self.element_factory.select(
            lambda e: (e.owner is None) and visible(e)
        ):
            model.add_element(element)

    @event_handler(DiagramSelectionChanged)
    def on_diagram_selection_changed(self, event):
        if not event.focused_item:
            return
        if element := event.focused_item.subject:
            self.select_element(element)
        else:
            return


class SearchEngine:
    def __init__(self, model, tree_view):
        self.model = model
        self.tree_view = tree_view
        self.selection = self.tree_view.get_model()
        self.selected_changed_id = self.selection.connect(
            "selection-changed", self.on_selection_changed
        )
        self.selected_item = None

    def on_selection_changed(self, selection, position, n_items):
        self.reset()

    def reset(self):
        self.selected_item = None

    def text_changed(self, search_text):
        if not self.selected_item:
            self.selected_item = self.selection.get_selected_item()
        if next_item := search(
            search_text,
            sorted_tree_walker(
                self.model,
                start_tree_item=self.selected_item and self.selected_item.get_item(),
                from_current=True,
            ),
        ):
            self.selection.handler_block(self.selected_changed_id)
            select_element(self.tree_view, next_item.element)
            self.selection.handler_unblock(self.selected_changed_id)

    def search_next(self, search_text):
        if next_item := search(
            search_text,
            sorted_tree_walker(
                self.model,
                start_tree_item=self.selection.get_selected_item().get_item(),
                from_current=False,
            ),
        ):
            select_element(self.tree_view, next_item.element)


def select_element(tree_view: Gtk.ListView, element: Element) -> int | None:
    def expand_up_to_element(element, expand=False) -> int | None:
        if not element:
            return 0
        if (n := expand_up_to_element(element.owner, expand=True)) is None:
            return None
        is_relationship = isinstance(element, UML.Relationship)
        while row := selection.get_item(n):
            if is_relationship and isinstance(row.get_item(), RelationshipItem):
                row.set_expanded(True)
            elif row.get_item().element is element:
                if expand:
                    row.set_expanded(True)
                return n
            n += 1
        return None

    selection = tree_view.get_model()
    pos = expand_up_to_element(element)
    if pos is not None:
        selection.set_selected(pos)
        tree_view.activate_action("list.scroll-to-item", GLib.Variant.new_uint32(pos))
    return pos


def create_search_bar(search_engine: SearchEngine):
    def on_search_changed(entry):
        search_engine.text_changed(entry.get_text())

    def on_stop_search(_entry):
        search_engine.reset()

    def on_search_next(entry):
        search_engine.search_next(entry.get_text())

    search_entry = Gtk.SearchEntry.new()
    search_entry.connect("search-changed", on_search_changed)
    search_entry.connect("stop-search", on_stop_search)
    search_entry.connect("activate", on_search_next)
    search_entry.connect("next-match", on_search_next)
    search_bar = Gtk.SearchBar.new()
    search_bar.set_child(search_entry)
    search_bar.connect_entry(search_entry)
    search_bar.set_show_close_button(True)

    return search_bar


def create_popup_controller(shortcuts):
    ctrl = Gtk.ShortcutController.new_for_model(shortcuts)
    ctrl.set_scope(Gtk.ShortcutScope.LOCAL)
    return ctrl


def list_item_factory_setup(_factory, list_item, event_manager, modeling_language):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        translated_ui_string("gaphor.ui", "treeitem.ui"),
        -1,
    )
    row = builder.get_object("row")

    def on_show_popup(ctrl, n_press, x, y):
        list_item.get_child().activate_action(
            "list.select-item",
            GLib.Variant.new_tuple(
                GLib.Variant.new_uint32(list_item.get_position()),
                GLib.Variant.new_boolean(False),
                GLib.Variant.new_boolean(False),
            ),
        )
        element = list_item.get_item().get_item().element
        if element:
            menu = Gtk.PopoverMenu.new_from_model(
                popup_model(element, modeling_language)
            )
            menu.set_parent(row)
            menu.popup()

    ctrl = Gtk.GestureClick.new()
    ctrl.set_button(Gdk.BUTTON_SECONDARY)
    ctrl.connect("pressed", on_show_popup)
    row.add_controller(ctrl)

    if sys.platform != "darwin":
        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        drag_source.connect("prepare", list_item_drag_prepare, list_item)
        drag_source.connect("drag-begin", list_item_drag_begin, list_item)
        row.add_controller(drag_source)

    drop_target = Gtk.DropTarget.new(ElementDragData.__gtype__, Gdk.DragAction.COPY)
    drop_target.set_preload(True)
    drop_target.connect("accept", list_item_drop_accept, list_item)
    drop_target.connect("motion", list_item_drop_motion, list_item)
    drop_target.connect("leave", list_item_drop_leave, list_item)
    drop_target.connect("drop", list_item_drop_drop, list_item, event_manager)
    row.add_controller(drop_target)

    text = builder.get_object("text")

    should_commit = True

    def end_editing():
        list_item.get_item().get_item().visible_child_name = "default"
        row.get_parent().grab_focus()

    def text_focus_out(ctrl):
        if should_commit:
            edit_text = text.get_buffer().get_text()
            tree_item = list_item.get_item().get_item()
            with Transaction(event_manager):
                tree_item.edit_text = edit_text
        end_editing()

    def text_key_pressed(ctrl, keyval, keycode, state):
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            end_editing()
            return True
        elif keyval == Gdk.KEY_Escape:
            nonlocal should_commit
            should_commit = False
            list_item.get_item().get_item().sync()
            end_editing()
            return True
        return False

    focus_ctrl = Gtk.EventControllerFocus.new()
    focus_ctrl.connect("leave", text_focus_out)
    text.add_controller(focus_ctrl)

    key_ctrl = Gtk.EventControllerKey.new()
    key_ctrl.connect("key-pressed", text_key_pressed)
    text.add_controller(key_ctrl)

    def start_editing(stack, pspec):
        nonlocal should_commit
        if stack.get_visible_child_name() == "editing":
            should_commit = True
            text.grab_focus()

    builder.get_object("stack").connect("notify::visible-child-name", start_editing)


def list_item_drag_prepare(
    source: Gtk.DragSource, x: int, y: int, list_item: Gtk.ListItem
) -> Gdk.ContentProvider | None:
    tree_item = list_item.get_item().get_item()
    if isinstance(tree_item, RelationshipItem):
        return None

    v = GObject.Value(
        ElementDragData.__gtype__, ElementDragData(element=tree_item.element)
    )
    return Gdk.ContentProvider.new_for_value(v)


def list_item_drag_begin(
    source: Gtk.DragSource, drag: Gdk.Drag, list_item: Gtk.ListItem
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
    style_context = widget.get_style_context()
    if y < 4:
        style_context.add_class("move-element-above")
    else:
        style_context.remove_class("move-element-above")

    return Gdk.DragAction.COPY


def list_item_drop_leave(
    target: Gtk.DropTarget, list_item: Gtk.ListItem
) -> Gdk.DragAction:
    widget = target.get_widget()
    style_context = widget.get_style_context()
    style_context.remove_class("move-element-above")


def list_item_drop_drop(
    target: Gtk.DropTarget,
    value: ElementDragData,
    x: int,
    y: int,
    list_item: Gtk.ListItem,
    event_manager,
) -> Gdk.DragAction:
    list_item_drop_leave(target, list_item)

    element = value.element
    tree_item = list_item.get_item().get_item()
    dest_element = tree_item.element
    if y < 4:
        dest_element = dest_element.owner

    with Transaction(event_manager) as tx:
        # This view is concerned with owner relationships.
        # Let's check if the owner relation has actually changed,
        # Otherwise roll back, to not confuse the user.
        if not change_owner(dest_element, element):
            tx.rollback()
        else:
            return True

    return False
