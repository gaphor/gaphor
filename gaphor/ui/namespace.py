"""This is the TreeView that is most common (for example: it is used in
Rational Rose).

This is a tree based on namespace relationships. As a result only
classifiers are shown here.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from gaphor import UML
from gaphor.core import action, event_handler, gettext, transactional
from gaphor.core.format import format, parse
from gaphor.core.modeling import (
    AttributeUpdated,
    DerivedSet,
    Diagram,
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
)
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import create_action_group
from gaphor.ui.event import DiagramOpened
from gaphor.ui.iconname import get_icon_name

if TYPE_CHECKING:
    from gaphor.core.eventmanager import EventManager
    from gaphor.core.modeling import ElementFactory


log = logging.getLogger(__name__)


class RELATIONSHIPS:
    name = "0"
    owner = None


def relationship_iter(model, iter):
    if iter is None or isinstance(model.get_value(iter, 0), UML.Package):
        child_iter = model.iter_children(iter)
        while child_iter:
            maybe_relationships = model.get_value(child_iter, 0)
            if maybe_relationships is RELATIONSHIPS:
                return child_iter
            child_iter = model.iter_next(child_iter)
        return model.append(iter, [RELATIONSHIPS])
    else:
        return iter


def relationship_iter_parent(model, iter):
    while model.get_value(iter, 0) is RELATIONSHIPS:
        iter = model.iter_parent(iter)
    return iter


class NamespaceView(Gtk.TreeView):

    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", 0, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", 0, TARGET_STRING),
        Gtk.TargetEntry.new("gaphor/element-id", 0, TARGET_ELEMENT_ID),
    ]

    def __init__(self, model: Gtk.TreeModel, element_factory: ElementFactory):
        Gtk.TreeView.__init__(self)
        self.set_model(model)
        self.element_factory = element_factory

        self.set_property("headers-visible", False)
        self.set_property("search-column", 0)

        selection = self.get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        column = Gtk.TreeViewColumn.new()
        # First cell in the column is for an image...
        cell = Gtk.CellRendererPixbuf()
        column.pack_start(cell, 0)
        column.set_cell_data_func(cell, self._set_pixbuf, None)

        # Second cell if for the name of the object...
        cell = Gtk.CellRendererText()
        cell.connect("edited", self._text_edited)
        column.pack_start(cell, 0)
        column.set_cell_data_func(cell, self._set_text, None)

        self.append_column(column)

        # drag
        self.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
            NamespaceView.DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        self.connect("drag-begin", NamespaceView.on_drag_begin)
        self.connect("drag-data-get", NamespaceView.on_drag_data_get)
        self.connect("drag-data-delete", NamespaceView.on_drag_data_delete)

        # drop
        self.drag_dest_set(
            Gtk.DestDefaults.ALL, [NamespaceView.DND_TARGETS[-1]], Gdk.DragAction.MOVE
        )
        self.connect("drag-motion", NamespaceView.on_drag_motion)
        self.connect("drag-data-received", NamespaceView.on_drag_data_received)

    def get_selected_element(self):
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return
        return model.get_value(iter, 0)

    def expand_root_nodes(self):
        self.expand_row(path=Gtk.TreePath.new_first(), open_all=False)

    def _set_pixbuf(self, column, cell, model, iter, data):
        element = model.get_value(iter, 0)

        if element is RELATIONSHIPS:
            cell.set_property("icon-name", None)
            cell.set_property("visible", False)
        elif isinstance(element, (UML.Property, UML.Operation)):
            cell.set_property("icon-name", None)
            cell.set_property("visible", False)
        else:
            icon_name = get_icon_name(element)
            cell.set_property("visible", True)

            if icon_name:
                cell.set_property("icon-name", icon_name)

    def _set_text(self, column, cell, model, iter, data):
        """Set font and of model elements in tree view."""
        element = model.get_value(iter, 0)

        cell.set_property(
            "weight",
            Pango.Weight.BOLD if isinstance(element, Diagram) else Pango.Weight.NORMAL,
        )

        cell.set_property(
            "style",
            Pango.Style.ITALIC
            if isinstance(element, (UML.Classifier, UML.BehavioralFeature))
            and element.isAbstract
            else Pango.Style.NORMAL,
        )

        if element is RELATIONSHIPS:
            text = gettext("<Relationships>")
        else:
            text = format(element) or "<None>"
        cell.set_property("text", text)

    @transactional
    def _text_edited(self, cell, path_str, new_text):
        """The text has been edited.

        This method updates the data object. Note that 'path_str' is a
        string where the fields are separated by colons ':', like this:
        '0:1:1'. We first turn them into a tuple.
        """
        model = self.get_property("model")
        iter = model.get_iter_from_string(path_str)
        element = model.get_value(iter, 0)
        try:
            parse(element, new_text)
        except TypeError:
            log.debug(f"No parser for {element}")

    def on_drag_begin(self, context):
        return True

    def on_drag_data_get(self, context, selection_data, info, time):
        """Get the data to be dropped by on_drag_data_received().

        We send the id of the dragged element.
        """
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if iter:
            element = model.get_value(iter, 0)
            if info == NamespaceView.TARGET_ELEMENT_ID:
                selection_data.set(
                    selection_data.get_target(), 8, str(element.id).encode()
                )
            else:
                selection_data.set(
                    selection_data.get_target(), 8, str(element.name).encode()
                )
        return True

    def on_drag_data_delete(self, context):
        """Delete data from original site, when `ACTION_MOVE` is used."""
        self.emit_stop_by_name("drag-data-delete")

    # Drop
    def on_drag_motion(self, context, x, y, time):
        path_pos_or_none = self.get_dest_row_at_pos(x, y)
        if path_pos_or_none:
            self.set_drag_dest_row(*path_pos_or_none)
        else:
            self.set_drag_dest_row(
                Gtk.TreePath.new_from_indices([len(self.get_model()) - 1]),
                Gtk.TreeViewDropPosition.AFTER,
            )
        return True

    @transactional
    def on_drag_data_received(self, context, x, y, selection, info, time):
        """Drop the data send by on_drag_data_get()."""
        self.stop_emission_by_name("drag-data-received")
        if info == NamespaceView.TARGET_ELEMENT_ID:
            element_id = selection.get_data().decode()
            drop_info = self.get_dest_row_at_pos(x, y)
        else:
            drop_info = None

        if drop_info:
            model = self.get_model()
            element = self.element_factory.lookup(element_id)
            assert isinstance(
                element, (Diagram, UML.Package, UML.Type)
            ), f"Element {element} can not be moved"
            path, position = drop_info
            iter = model.get_iter(path)
            dest_element = model.get_value(iter, 0)
            assert dest_element
            if dest_element is RELATIONSHIPS:
                iter = relationship_iter_parent(model, iter)
                dest_element = model.get_value(iter, 0)

            # Add the item to the parent if it is dropped on the same level,
            # else add it to the item.
            if position in (
                Gtk.TreeViewDropPosition.BEFORE,
                Gtk.TreeViewDropPosition.AFTER,
            ):
                parent_iter = model.iter_parent(iter)
                dest_element = (
                    None if parent_iter is None else model.get_value(parent_iter, 0)
                )
            try:
                # Check if element is part of the namespace of dest_element:
                ns = dest_element
                while ns:
                    if ns is element:
                        raise AttributeError
                    ns = ns.namespace

                # Set package. This only works for classifiers, packages and
                # diagrams. Properties and operations should not be moved.
                if dest_element is None:
                    del element.package
                else:
                    element.package = dest_element

            except AttributeError as e:
                log.info(f"Unable to drop data {e}")
                context.finish(False, False, time)
            else:
                context.finish(True, True, time)


class NamespaceModelRefreshed:
    def __init__(self, model):
        self.model = model


class NamespaceModel:
    def __init__(self, event_manager: EventManager, element_factory: ElementFactory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.model = Gtk.TreeStore.new([object])

        event_manager.subscribe(self.refresh)
        event_manager.subscribe(self._on_element_create)
        event_manager.subscribe(self._on_element_delete)
        event_manager.subscribe(self._on_association_set)
        event_manager.subscribe(self._on_attribute_change)

    def shutdown(self):
        em = self.event_manager
        em.unsubscribe(self.refresh)
        em.unsubscribe(self._on_element_create)
        em.unsubscribe(self._on_element_delete)
        em.unsubscribe(self._on_association_set)
        em.unsubscribe(self._on_attribute_change)

    def sorted(self):
        """Get a sorted version of this model."""
        sorted_model = Gtk.TreeModelSort(model=self.model)

        def sort_func(model, iter_a, iter_b, userdata):
            va = model.get_value(iter_a, 0)
            vb = model.get_value(iter_b, 0)

            # Put Relationships pseudo-node at top
            if va is RELATIONSHIPS:
                return -1
            if vb is RELATIONSHIPS:
                return 1

            a = (format(va) or "").lower()
            b = (format(vb) or "").lower()
            if a == b:
                return 0
            if a > b:
                return 1
            return -1

        sorted_model.set_sort_func(0, sort_func, None)
        sorted_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        return sorted_model

    def iter_children(self, iter):
        return self.model.iter_children(iter)

    def iter_n_children(self, iter):
        return self.model.iter_n_children(iter)

    def get_iter_first(self):
        return self.model.get_iter_first()

    def get_path(self, iter):
        return self.model.get_path(iter)

    def get_value(self, iter, column):
        return self.model.get_value(iter, column)

    def iter_for_element(self, element, old_owner=0):
        """Get the Gtk.TreeIter for an element in the Namespace.

        Args:
            element: The element contained in the in the Namespace.
            old_owner: The old owner containing the element, optional.

        Returns: Gtk.TreeIter object of the model (not the sorted one!)
        """

        # Using `0` as sentinel
        if old_owner != 0:
            parent_iter = self.iter_for_element(old_owner)
        elif element and element.owner:
            parent_iter = self.iter_for_element(element.owner)
        else:
            parent_iter = None

        if isinstance(element, UML.Relationship):
            parent_iter = relationship_iter(self.model, parent_iter)

        child_iter = self.model.iter_children(parent_iter)
        while child_iter:
            if self.model.get_value(child_iter, 0) is element:
                return child_iter
            child_iter = self.model.iter_next(child_iter)
        return None

    def _visible(self, element):
        """Special case: Non-navigable properties."""
        return isinstance(
            element, (UML.Relationship, UML.NamedElement)
        ) and not isinstance(
            element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
        )

    def _add(self, element, iter=None):
        if self._visible(element):
            if isinstance(element, UML.Relationship):
                iter = relationship_iter(self.model, iter)
            child_iter = self.model.append(iter, [element])
            for e in element.ownedElement:
                # check if owned element is indeed within parent's owner
                # This is important since we should be able to traverse this relation both ways
                if element is e.owner:
                    self._add(e, child_iter)

    def _remove(self, iter):
        if iter:
            parent_iter = self.model.iter_parent(iter)
            self.model.remove(iter)
            if (
                parent_iter
                and not self.model.iter_has_child(parent_iter)
                and self.model.get_value(parent_iter, 0) is RELATIONSHIPS
            ):
                self.model.remove(parent_iter)

    @event_handler(ModelReady, ModelFlushed)
    def refresh(self, event=None):
        """Load a new model completely."""
        log.info("Rebuilding namespace model")

        self.model.clear()

        toplevel = self.element_factory.select(
            lambda e: self._visible(e) and not e.owner
        )

        for element in toplevel:
            if self._visible(element):
                self._add(element)

        self.event_manager.handle(NamespaceModelRefreshed(self))

    @event_handler(ElementCreated)
    def _on_element_create(self, event: ElementCreated):
        element = event.element
        if self._visible(element) and not self.iter_for_element(element):
            iter = self.iter_for_element(element.owner)
            self._add(element, iter)

    @event_handler(ElementDeleted)
    def _on_element_delete(self, event: ElementDeleted):
        element = event.element
        iter = self.iter_for_element(element)
        self._remove(iter)

    @event_handler(DerivedSet)
    def _on_association_set(self, event: DerivedSet):
        if event.property is not UML.Element.owner:
            return
        old_value, new_value = event.old_value, event.new_value

        element = event.element
        old_iter = self.iter_for_element(element, old_owner=old_value)
        self._remove(old_iter)

        if self._visible(element):
            new_iter = self.iter_for_element(new_value)
            # Should be either set (sub node) or unset (root node)
            if bool(new_iter) == bool(new_value):
                self._add(element, new_iter)

    @event_handler(AttributeUpdated)
    def _on_attribute_change(self, event: AttributeUpdated):
        """Element changed, update appropriate row."""
        if (
            event.property is UML.Classifier.isAbstract
            or event.property is UML.BehavioralFeature.isAbstract
            or event.property is UML.NamedElement.name
        ):
            element = event.element

            iter = self.iter_for_element(element)
            if iter:
                path = self.model.get_path(iter)
                self.model.row_changed(path, iter)


class Namespace(UIComponent):
    def __init__(self, event_manager: EventManager, element_factory: ElementFactory):
        self.event_manager = event_manager
        self.element_factory = element_factory

        self.model: Optional[NamespaceModel] = None
        self.view: Optional[NamespaceView] = None

    def open(self):
        self.model = NamespaceModel(self.event_manager, self.element_factory)
        self.event_manager.subscribe(self._on_model_refreshed)

        sorted_model = self.model.sorted()

        def search_func(model, column, key, rowiter):
            # Note that this function returns `False` for a match!
            assert column == 0
            row = model[rowiter]
            matched = False

            # Search in child rows.  If any element in the underlying
            # tree matches, it will expand.
            for inner in row.iterchildren():
                if not search_func(model, column, key, inner.iter):
                    view.expand_to_path(row.path)
                    matched = True

            element = list(row)[column]
            s = format(element)
            if s and key.lower() in s.lower():
                matched = True
            elif not matched:
                view.collapse_row(row.path)

            return not matched  # False means match found!

        view = NamespaceView(sorted_model, self.element_factory)
        view.set_search_equal_func(search_func)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(view)
        scrolled_window.show()
        view.show()

        scrolled_window.insert_action_group(
            "tree-view", create_action_group(self, "tree-view")[0]
        )
        view.connect_after("event-after", self._on_view_event)
        view.connect("row-activated", self._on_view_row_activated)
        view.connect_after("cursor-changed", self._on_view_cursor_changed)
        view.connect("destroy", self._on_view_destroyed)
        self.view = view
        self.model.refresh()

        return scrolled_window

    def close(self):
        if self.view:
            self.view.destroy()
            self.view = None
        if self.model:
            self.model.shutdown()
            self.model = None
        self.event_manager.unsubscribe(self._on_model_refreshed)

    def namespace_popup_model(self):
        assert self.view
        model = Gio.Menu.new()

        part = Gio.Menu.new()
        part.append(gettext("_Open"), "tree-view.open")
        part.append(gettext("_Rename"), "tree-view.rename")
        model.append_section(None, part)

        part = Gio.Menu.new()
        part.append(gettext("New _Diagram"), "tree-view.create-diagram")
        part.append(gettext("New _Package"), "tree-view.create-package")
        model.append_section(None, part)

        part = Gio.Menu.new()
        part.append(gettext("De_lete"), "tree-view.delete")
        model.append_section(None, part)

        element = self.view.get_selected_element()

        part = Gio.Menu.new()
        for presentation in element.presentation:
            diagram = presentation.diagram
            menu_item = Gio.MenuItem.new(
                gettext('Show in "{diagram}"').format(diagram=diagram.name),
                "tree-view.show-in-diagram",
            )
            menu_item.set_attribute_value("target", GLib.Variant.new_string(diagram.id))
            part.append_item(menu_item)

            # Play it safe with an (arbitrary) upper bound
            if part.get_n_items() > 29:
                break

        if part.get_n_items() > 0:
            model.append_section(None, part)
        return model

    @event_handler(NamespaceModelRefreshed)
    def _on_model_refreshed(self, event):
        # Expand all root elements:
        if self.view:
            self.view.expand_root_nodes()
            self._on_view_cursor_changed(self.view)

    def _on_view_event(self, view, event):
        """Show a popup menu if button3 was pressed on the TreeView."""
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button.button == 3:
            menu = Gtk.Menu.new_from_model(self.namespace_popup_model())
            menu.attach_to_widget(view, None)
            menu.popup_at_pointer(event)
        elif event.type == Gdk.EventType.KEY_PRESS and event.key.keyval == Gdk.KEY_F2:
            self.tree_view_rename_selected()

    def _on_view_row_activated(self, view, path, column):
        """Double click on an element in the tree view."""
        view.get_action_group("tree-view").lookup_action("open").activate()

    def _on_view_cursor_changed(self, view):
        """Another row is selected, toggle action sensitivity."""
        element = view.get_selected_element()
        action_group = view.get_action_group("tree-view")
        if element is RELATIONSHIPS:
            action_group.lookup_action("create-diagram").set_enabled(True)
            action_group.lookup_action("create-package").set_enabled(True)
            action_group.lookup_action("delete").set_enabled(False)
            action_group.lookup_action("rename").set_enabled(False)
            return

        action_group.lookup_action("open").set_enabled(isinstance(element, Diagram))
        action_group.lookup_action("create-diagram").set_enabled(
            isinstance(element, UML.Package)
            or (element and isinstance(element.owner, UML.Package))
        )
        action_group.lookup_action("create-package").set_enabled(
            isinstance(element, UML.Package)
        )
        action_group.lookup_action("delete").set_enabled(
            isinstance(element, Diagram)
            or (isinstance(element, UML.Package) and not element.presentation)
        )
        action_group.lookup_action("rename").set_enabled(
            isinstance(element, UML.NamedElement)
        )

    def _on_view_destroyed(self, widget):
        self.close()

    def select_element(self, element):
        """Select an element from the Namespace view.

        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if
        it's a Diagram).
        """
        assert self.model
        assert self.view

        model = self.view.get_model()
        child_iter = self.model.iter_for_element(element)
        ok, tree_iter = model.convert_child_iter_to_iter(child_iter)
        assert ok, "Could not convert model iterator to view"
        path = model.get_path(tree_iter)
        path_indices = path.get_indices()

        # Expand the parent row
        if len(path_indices) > 1:
            parent_path = Gtk.TreePath.new_from_indices(path_indices[:-1])
            self.view.expand_row(path=parent_path, open_all=False)

        selection = self.view.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self.view)

    @action(name="tree-view.open")
    def tree_view_open_selected(self):
        assert self.view
        element = self.view.get_selected_element()
        if isinstance(element, Diagram):
            self.event_manager.handle(DiagramOpened(element))
        else:
            log.debug(f"No action defined for element {type(element).__name__}")

    @action(name="tree-view.show-in-diagram")
    def tree_view_show_in_diagram(self, diagam_id: str):
        element = self.element_factory.lookup(diagam_id)
        self.event_manager.handle(DiagramOpened(element))

    @action(name="tree-view.rename", shortcut="F2")
    def tree_view_rename_selected(self):
        assert self.view
        view = self.view
        element = view.get_selected_element()
        if element not in (None, RELATIONSHIPS):
            selection = view.get_selection()
            model, iter = selection.get_selected()
            path = model.get_path(iter)
            column = view.get_column(0)
            cell = column.get_cells()[1]
            cell.set_property("editable", 1)
            view.set_cursor(path, column, True)
            cell.set_property("editable", 0)

    @action(name="tree-view.create-diagram")
    @transactional
    def tree_view_create_diagram(self):
        assert self.view
        element = self.view.get_selected_element()
        while not isinstance(element, UML.Package):
            element = element.namespace
        diagram = self.element_factory.create(Diagram)
        diagram.package = element

        diagram.name = f"{element.name} diagram" if element else "New diagram"
        self.select_element(diagram)
        self.event_manager.handle(DiagramOpened(diagram))
        self.tree_view_rename_selected()

    @action(name="tree-view.create-package")
    @transactional
    def tree_view_create_package(self):
        assert self.view
        element = self.view.get_selected_element()
        package = self.element_factory.create(UML.Package)
        package.package = element

        package.name = f"{element.name} package" if element else "New model"
        self.select_element(package)
        self.tree_view_rename_selected()

    @action(name="tree-view.delete")
    @transactional
    def tree_view_delete(self):
        assert self.view
        element = self.view.get_selected_element()
        if isinstance(element, UML.Package):
            element.unlink()
        elif isinstance(element, Diagram):
            m = Gtk.MessageDialog(
                None,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "Do you really want to delete diagram %s?\n\n"
                "This will possibly delete diagram items\n"
                "that are not shown in other diagrams." % (element.name or "<None>"),
            )
            if m.run() == Gtk.ResponseType.YES:
                for i in reversed(element.canvas.get_all_items()):
                    s = i.subject
                    if s and len(s.presentation) == 1:
                        s.unlink()
                    i.unlink()
                element.unlink()
            m.destroy()
