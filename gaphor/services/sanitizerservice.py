"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from logging import getLogger


from gaphor import UML
from gaphor.UML.event import AssociationDeleteEvent, AssociationSetEvent
from gaphor.core import inject, event_handler
from gaphor.abc import Service


class SanitizerService(Service):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """

    def __init__(self, event_manager):
        self.event_manager = event_manager

        event_manager.subscribe(self._unlink_on_presentation_delete)
        event_manager.subscribe(self._unlink_on_stereotype_delete)
        event_manager.subscribe(self._unlink_on_extension_delete)
        event_manager.subscribe(self._disconnect_extension_end)

    def init(self, app=None):
        pass

    def shutdown(self):
        self.event_manager.unsubscribe(self._unlink_on_presentation_delete)
        self.event_manager.unsubscribe(self._unlink_on_stereotype_delete)
        self.event_manager.unsubscribe(self._unlink_on_extension_delete)
        self.event_manager.unsubscribe(self._disconnect_extension_end)

    @event_handler(AssociationDeleteEvent)
    def _unlink_on_presentation_delete(self, event):
        """
        Unlink the model element if no more presentations link to the `item`'s
        subject or the deleted item was the only item currently linked.
        """
        if event.property is UML.Element.presentation:
            old_presentation = event.old_value
            if old_presentation and not event.element.presentation:
                event.element.unlink()

    def perform_unlink_for_instances(self, st, meta):

        inst = UML.model.find_instances(st)

        for i in list(inst):
            for e in i.extended:
                if not meta or isinstance(e, meta):
                    i.unlink()

    @event_handler(AssociationDeleteEvent)
    def _unlink_on_extension_delete(self, event):
        """
        Remove applied stereotypes when extension is deleted.
        """
        if (
            isinstance(event.element, UML.Extension)
            and event.property is UML.Association.memberEnd
            and event.element.memberEnd
        ):
            p = event.element.memberEnd[0]
            ext = event.old_value
            if isinstance(p, UML.ExtensionEnd):
                p, ext = ext, p
            st = ext.type
            meta = p.type and getattr(UML, p.type.name, None)
            if st:
                self.perform_unlink_for_instances(st, meta)

    @event_handler(AssociationSetEvent)
    def _disconnect_extension_end(self, event):
        if event.property is UML.ExtensionEnd.type and event.old_value:
            ext = event.element
            p = ext.opposite
            if not p:
                return
            st = event.old_value
            meta = getattr(UML, p.type.name, None)
            if st:
                self.perform_unlink_for_instances(st, meta)

    @event_handler(AssociationDeleteEvent)
    def _unlink_on_stereotype_delete(self, event):
        """
        Remove applied stereotypes when stereotype is deleted.
        """
        if event.property is UML.InstanceSpecification.classifier:
            if isinstance(event.old_value, UML.Stereotype):
                event.element.unlink()
