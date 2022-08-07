"""The Sanitize module is dedicated to adapters (stuff) that keeps the model
clean and in sync with diagrams."""


from typing import Iterable

from gaphor import UML
from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.core.modeling.event import AssociationDeleted, AssociationSet, DerivedSet
from gaphor.diagram.deletable import deletable
from gaphor.diagram.general import CommentLineItem
from gaphor.event import Notification
from gaphor.i18n import gettext


def undo_guard(func):
    """Do not execute the sanitizer if we're undoing a transaction.

    The sanitizer actions are already part of that transaction.
    """

    def guard(self, event):
        if self.undo_manager and self.undo_manager.in_undo_transaction():
            return
        return func(self, event)

    return guard


class SanitizerService(Service):
    """Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some)."""

    def __init__(self, event_manager, undo_manager=None, properties=None):
        self.event_manager = event_manager
        self.properties = properties or {}
        self.undo_manager = undo_manager

        event_manager.subscribe(self._unlink_on_subject_delete)
        event_manager.subscribe(self.update_annotated_element_link)
        event_manager.subscribe(self._unlink_on_extension_delete)
        event_manager.subscribe(self._redraw_diagram_on_move)

    def shutdown(self):
        event_manager = self.event_manager
        event_manager.unsubscribe(self._unlink_on_subject_delete)
        event_manager.unsubscribe(self.update_annotated_element_link)
        event_manager.unsubscribe(self._unlink_on_extension_delete)
        event_manager.unsubscribe(self._redraw_diagram_on_move)

    @event_handler(AssociationSet)
    @undo_guard
    def _unlink_on_subject_delete(self, event):
        """Unlink the model element if no more presentations link to the
        `item`'s subject or the deleted item was the only item currently
        linked."""
        if (
            not self.properties.get("remove-unused-elements", True)
            or event.property is not Presentation.subject  # type: ignore[misc]
        ):
            return

        old_subject = event.old_value
        if old_subject and not old_subject.presentation and deletable(old_subject):
            old_subject.unlink()

            self.event_manager.handle(
                Notification(
                    gettext(
                        "Removed unused elements from the model: they are not used in any other diagram."
                    )
                )
            )

    @event_handler(AssociationSet)
    @undo_guard
    def update_annotated_element_link(self, event):
        """Link comment and element if a comment line is present, but comment
        and element subject are not connected yet."""
        if event.property is not Presentation.subject:  # type: ignore[misc]
            return

        element: Presentation = event.element
        subject = event.new_value
        if not (element.diagram and subject):
            return

        for cinfo in element.diagram.connections.get_connections(connected=element):
            comment_line = cinfo.item
            if not isinstance(comment_line, CommentLineItem):
                continue
            opposite = comment_line.opposite(cinfo.handle)
            opposite_cinfo = element.diagram.connections.get_connection(opposite)
            if not opposite_cinfo:
                continue
            comment_item = opposite_cinfo.connected
            comment = comment_item.subject
            comment.annotatedElement = subject

    @event_handler(AssociationDeleted)
    @undo_guard
    def _unlink_on_extension_delete(self, event):
        """Remove applied stereotypes when extension is deleted."""
        if isinstance(event.element, UML.Stereotype) and event.property in (
            UML.Stereotype.ownedAttribute,
            UML.Stereotype.generalization,
        ):
            update_stereotype_application(event.element)

    @event_handler(DerivedSet)
    @undo_guard
    def _redraw_diagram_on_move(self, event):
        if event.property is Element.owner and isinstance(event.element, Diagram):
            diagram = event.element
            for item in diagram.get_all_items():
                diagram.request_update(item)


def update_stereotype_application(stereotype: UML.Stereotype, seen=None):
    # Seen is a (mutable) list to avoid infinite loops
    if seen is None:
        seen = {stereotype}

    metaclass_names = {m.name for m in metaclasses(stereotype)}

    for instance_spec in list(stereotype.instanceSpecification):
        for e in list(instance_spec.extended):
            names = {c.__name__ for c in type(e).__mro__ if issubclass(c, Element)}
            if names.isdisjoint(metaclass_names):
                del instance_spec.extended[e]
        if not instance_spec.extended:
            instance_spec.unlink()

    for sub_stereotype in stereotype.specialization[:].specific:
        if sub_stereotype not in seen:
            seen.add(sub_stereotype)
            update_stereotype_application(sub_stereotype, seen)


def metaclasses(stereotype: UML.Stereotype, seen=None) -> Iterable[UML.Class]:
    # Seen is a (mutable) list to avoid infinite loops
    if seen is None:
        seen = {stereotype}

    extensions = (
        e
        for e in stereotype.ownedAttribute[:].association
        if isinstance(e, UML.Extension)
    )

    yield from (e.metaclass for e in extensions if e.metaclass)

    for super_stereotype in stereotype.generalization[:].general:
        if super_stereotype not in seen:
            seen.add(super_stereotype)
            yield from metaclasses(super_stereotype, seen)
