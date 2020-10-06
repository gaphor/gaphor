from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import event_handler
from gaphor.core.format import format
from gaphor.core.modeling import (
    AttributeUpdated,
    DerivedSet,
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
)

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

    def get_element(self, iter):
        return self.model.get_value(iter, 0)

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
            parent_iter = relationship_iter(self.model, parent_iter)

        child_iter = self.model.iter_children(parent_iter)
        while child_iter:
            if self.model.get_value(child_iter, 0) is element:
                return child_iter
            child_iter = self.model.iter_next(child_iter)
        return None

    def _visible(self, element):
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
