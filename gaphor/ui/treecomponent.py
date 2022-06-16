from __future__ import annotations

from gaphas.decorators import g_async
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


class TreeComponent(UIComponent, ActionProvider):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.model = TreeModel()

    def open(self):
        self.event_manager.subscribe(self.on_element_created)
        self.event_manager.subscribe(self.on_element_deleted)
        self.event_manager.subscribe(self.on_owner_changed)
        self.event_manager.subscribe(self.on_owned_element_changed)
        self.event_manager.subscribe(self.on_attribute_changed)
        self.event_manager.subscribe(self.on_model_ready)
        self.event_manager.subscribe(self.on_diagram_selection_changed)

        self.search_bar, self.search_filter = create_search_bar()

        tree_model = Gtk.TreeListModel.new(
            self.model.root,
            passthrough=False,
            autoexpand=False,
            create_func=self.model.child_model,
            user_data=None,
        )

        self.sorter = Gtk.CustomSorter.new(tree_item_sort)
        tree_sorter = Gtk.TreeListRowSorter.new(self.sorter)
        self.sort_model = Gtk.SortListModel.new(tree_model, tree_sorter)
        self.selection = Gtk.SingleSelection.new(
            Gtk.FilterListModel.new(self.sort_model, self.search_filter)
        )
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
        self.create_gtk4_popup_controller(shortcuts)

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

    def create_gtk4_popup_controller(self, shortcuts):
        ctrl = Gtk.ShortcutController.new_for_model(shortcuts)
        ctrl.set_scope(Gtk.ShortcutScope.LOCAL)
        self.tree_view.add_controller(ctrl)

    def select_element(self, element: Element) -> int | None:
        def expand_up_to_element(element, expand=False) -> int | None:
            if not element:
                return 0
            if (n := expand_up_to_element(element.owner, expand=True)) is None:
                return None
            is_relationship = isinstance(element, UML.Relationship)
            while row := self.sort_model.get_item(n):
                if is_relationship and isinstance(row.get_item(), RelationshipItem):
                    row.set_expanded(True)
                elif row.get_item().element is element:
                    if expand:
                        row.set_expanded(True)
                    return n
                n += 1
            return None

        pos = expand_up_to_element(element)
        if pos is not None:
            self.selection.set_selected(pos)
            self.tree_view.activate_action(
                "list.scroll-to-item", GLib.Variant.new_uint32(pos)
            )
        return pos

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
    @g_async(single=True)
    def tree_view_rename_selected(self):
        if row_item := self.selection.get_selected_item():
            tree_item: TreeItem = row_item.get_item()
            tree_item.start_editing()

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
        element = event.focused_item.subject
        if not element:
            return

        self.select_element(element)


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "treeitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


def create_search_bar():
    search_text: str = ""

    def on_search_changed(entry):
        nonlocal search_text
        filter_change = (
            Gtk.FilterChange.MORE_STRICT
            if search_text in entry.get_text()
            else Gtk.FilterChange.MORE_STRICT
            if entry.get_text() in search_text
            else Gtk.FilterChange.DIFFERENT
        )
        search_text = entry.get_text()
        search_filter.changed(filter_change)

    def on_stop_search(_entry):
        nonlocal search_text
        search_text = ""
        search_filter.changed(Gtk.FilterChange.LESS_STRICT)

    def name_filter(item):
        item = item.get_item()
        return isinstance(item, TreeItem) and search_text.lower() in item.text.lower()

    search_filter = Gtk.CustomFilter.new(name_filter)
    search_entry = Gtk.SearchEntry.new()
    search_entry.connect("search-changed", on_search_changed)
    search_entry.connect("stop-search", on_stop_search)
    search_bar = Gtk.SearchBar.new()
    search_bar.set_child(search_entry)
    search_bar.connect_entry(search_entry)
    search_bar.set_show_close_button(True)

    return search_bar, search_filter


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
        element = list_item.get_item().get_item().element
        menu = Gtk.PopoverMenu.new_from_model(popup_model(element, modeling_language))
        menu.set_parent(row)
        menu.popup()

    ctrl = Gtk.GestureClick.new()
    ctrl.set_button(Gdk.BUTTON_SECONDARY)
    ctrl.connect("pressed", on_show_popup)
    row.add_controller(ctrl)

    drag_source = Gtk.DragSource.new()
    drag_source.set_actions(Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
    drag_source.connect("prepare", list_item_drag_prepare, list_item)
    row.add_controller(drag_source)

    drop_target = Gtk.DropTarget.new(ElementDragData.__gtype__, Gdk.DragAction.COPY)
    drop_target.set_preload(True)
    drop_target.connect("accept", list_item_drop_accept, list_item)
    drop_target.connect("motion", list_item_drop_motion, list_item)
    drop_target.connect("leave", list_item_drop_leave, list_item)
    drop_target.connect("drop", list_item_drop_drop, list_item, event_manager)
    row.add_controller(drop_target)

    def end_editing():
        list_item.get_item().get_item().visible_child_name = "default"
        row.get_parent().grab_focus()

    def text_activate(widget):
        text = widget.get_buffer().get_text()
        tree_item = list_item.get_item().get_item()
        with Transaction(event_manager):
            tree_item.edit_text = text
        end_editing()

    def text_focus_out(widget, pspec):
        if not widget.has_focus():
            text_activate(text)

    def text_escape(widget, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            list_item.get_item().get_item().sync()
            end_editing()

    text = builder.get_object("text")
    text.connect("notify::has-focus", text_focus_out)
    text.connect("activate", text_activate)
    controller = Gtk.EventControllerKey.new()
    controller.connect("key-pressed", text_escape)
    text.add_controller(controller)

    def stack_changed(stack, pspec):
        if stack.get_visible_child_name() == "editing":
            text.grab_focus()

    builder.get_object("stack").connect("notify::visible-child-name", stack_changed)


def list_item_drag_prepare(
    source: Gtk.DragSource, x: int, y: int, list_item: Gtk.ListItem
) -> Gdk.ContentProvider | None:
    tree_item = list_item.get_item().get_item()
    if isinstance(tree_item, RelationshipItem):
        return None

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

    v = GObject.Value(
        ElementDragData.__gtype__, ElementDragData(element=tree_item.element)
    )
    return Gdk.ContentProvider.new_for_value(v)


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
