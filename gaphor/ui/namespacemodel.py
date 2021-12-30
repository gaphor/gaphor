from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gaphas.decorators import g_async
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import Transaction, event_handler, gettext
from gaphor.core.format import format
from gaphor.core.modeling import (
    AttributeUpdated,
    DerivedSet,
    Diagram,
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
)
from gaphor.event import Notification

if TYPE_CHECKING:
    from gaphor.core.eventmanager import EventManager
    from gaphor.core.modeling import ElementFactory


log = logging.getLogger(__name__)


class RELATIONSHIPS:
    name = "0"
    owner = None


def relationship_iter(model, iter):
    if iter is not None and not isinstance(model.get_value(iter, 0), UML.Package):
        return iter

    child_iter = model.iter_children(iter)
    while child_iter:
        maybe_relationships = model.get_value(child_iter, 0)
        if maybe_relationships is RELATIONSHIPS:
            return child_iter
        child_iter = model.iter_next(child_iter)
    return model.append(iter, [RELATIONSHIPS])


def relationship_iter_parent(model, iter):
    while model.get_value(iter, 0) is RELATIONSHIPS:
        iter = model.iter_parent(iter)
    return iter


class NamespaceModelRefreshed:
    def __init__(self, model):
        self.model = model


class NamespaceModelElementDropped:
    def __init__(self, model, element):
        self.model = model
        self.element = element


class NamespaceModel(Gtk.TreeStore):
    def __init__(self, event_manager: EventManager, element_factory: ElementFactory):
        super().__init__(object)
        self.event_manager = event_manager
        self.element_factory = element_factory

        event_manager.subscribe(self.refresh)
        event_manager.subscribe(self._on_element_create)
        event_manager.subscribe(self._on_element_delete)
        event_manager.subscribe(self._on_association_set)
        event_manager.subscribe(self._on_attribute_change)

        self.set_sort_func(0, sort_func, None)
        self.set_sort_column_id(0, Gtk.SortType.ASCENDING)

    def shutdown(self):
        em = self.event_manager
        em.unsubscribe(self.refresh)
        em.unsubscribe(self._on_element_create)
        em.unsubscribe(self._on_element_delete)
        em.unsubscribe(self._on_association_set)
        em.unsubscribe(self._on_attribute_change)

    def get_element(self, iter):
        return self.get_value(iter, 0)

    def iter_for_element(self, element, old_owner=0):
        """Get the Gtk.TreeIter for an element in the Namespace.

        Args:
            element: The element contained in the Namespace.
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
            parent_iter = relationship_iter(self, parent_iter)

        child_iter = self.iter_children(parent_iter)
        while child_iter:
            if self.get_value(child_iter, 0) is element:
                return child_iter
            child_iter = self.iter_next(child_iter)
        return None

    def _visible(self, element):
        return isinstance(
            element, (UML.Relationship, UML.NamedElement, Diagram)
        ) and not isinstance(
            element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
        )

    def _add(self, element, iter=None):
        if self._visible(element):
            if isinstance(element, UML.Relationship):
                iter = relationship_iter(self, iter)
            child_iter = self.append(iter, [element])
            for e in element.ownedElement:
                # check if owned element is indeed within parent's owner
                # This is important since we should be able to traverse this relation both ways
                if element is e.owner:
                    self._add(e, child_iter)

    def _remove(self, iter):
        if iter:
            parent_iter = self.iter_parent(iter)
            self.remove(iter)
            if (
                parent_iter
                and not self.iter_has_child(parent_iter)
                and self.get_value(parent_iter, 0) is RELATIONSHIPS
            ):
                self.remove(parent_iter)

    @event_handler(ModelReady, ModelFlushed)
    def refresh(self, event=None):
        """Load a new model completely."""
        log.debug("Rebuilding namespace model")

        self.clear()

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
            or event.property is Diagram.name
            or event.property is UML.NamedElement.name
        ):
            element = event.element

            iter = self.iter_for_element(element)
            if iter:
                path = self.get_path(iter)
                self.row_changed(path, iter)
                self.sort()

    @g_async(single=True)
    def sort(self):
        self.set_sort_column_id(
            Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, Gtk.SortType.ASCENDING
        )
        self.set_sort_column_id(0, Gtk.SortType.ASCENDING)

    def do_row_draggable(self, path):
        return True

    def do_drag_data_get(self, path, selection_data):
        target = str(selection_data.get_target())
        row = self[path]
        element = row[0]
        if target == "GTK_TREE_MODEL_ROW":
            return Gtk.tree_set_row_drag_data(selection_data, self, path)
        elif target == "gaphor/element-id":
            selection_data.set(selection_data.get_target(), 8, str(element.id).encode())
            return True
        return False

    def do_drag_data_delete(self, path):
        return False

    def do_row_drop_possible(self, dest_path, selection_data):
        src_data = Gtk.tree_get_row_drag_data(selection_data)
        if not src_data:
            return False
        ok, src_model, src_path = src_data
        if not ok or src_model is not self:
            log.warning("DnD from different tree model")
            return False

        src_row = self[src_path]
        element = src_row[0]

        return isinstance(element, (Diagram, UML.Package, UML.Type))

    def do_drag_data_received(self, dest_path, selection_data):
        if str(selection_data.get_target()) != "GTK_TREE_MODEL_ROW":
            log.warning(f"Wrong drag data type {selection_data.get_target()}")
            return False

        ok, src_model, src_path = Gtk.tree_get_row_drag_data(selection_data)
        if not ok or src_model is not self:
            log.debug("Can't DnD from different tree model")
            return False

        src_row = self[src_path]
        element = src_row[0]

        dest_path.up()
        if not dest_path:
            dest_element = None
        else:
            try:
                iter = self.get_iter(dest_path)
            except ValueError:
                log.debug(f"Invalid path: '{dest_path}'")
                return False

            dest_element = self.get_value(iter, 0)

            if dest_element is RELATIONSHIPS:
                iter = relationship_iter_parent(self, iter)
                dest_element = self.get_value(iter, 0)

            if element.owner is dest_element:
                return False

            # Check if element is part of the namespace of dest_element:
            ns = dest_element
            while ns:
                if ns is element:
                    log.info("Can not create a cycle")
                    return False
                ns = ns.owner

        try:
            # Set package. This only works for classifiers, packages and
            # diagrams. Properties and operations should not be moved.
            with Transaction(self.event_manager):
                if dest_element is None and isinstance(element, Diagram):
                    del element.element
                elif dest_element is None:
                    del element.package
                elif isinstance(element, Diagram):
                    element.element = dest_element
                else:
                    element.package = dest_element
                self.event_manager.handle(NamespaceModelElementDropped(self, element))
            return True
        except (AttributeError, TypeError) as e:
            self.namespace_exception(dest_element, e, element)
        return False

    def namespace_exception(self, dest_element, e, element):
        log.info(f"Unable to drop data {e}")
        self.event_manager.handle(
            Notification(
                gettext("A {} can’t be part of a {}.").format(
                    type(element).__name__, type(dest_element).__name__
                )
            )
        )


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
