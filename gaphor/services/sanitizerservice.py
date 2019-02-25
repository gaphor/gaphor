"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from logging import getLogger
from zope import component

from zope.interface import implementer

from gaphor import UML
from gaphor.UML.interfaces import IAssociationDeleteEvent, IAssociationSetEvent
from gaphor.core import inject
from gaphor.interfaces import IService


@implementer(IService)
class SanitizerService(object):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """

    logger = getLogger("Sanitizer")

    component_registry = inject("component_registry")
    element_factory = inject("element_factory")
    property_dispatcher = inject("property_dispatcher")

    def __init__(self):
        pass

    def init(self, app=None):
        self.component_registry.register_handler(self._unlink_on_presentation_delete)
        self.component_registry.register_handler(self._unlink_on_stereotype_delete)
        self.component_registry.register_handler(self._unlink_on_extension_delete)
        self.component_registry.register_handler(self._disconnect_extension_end)

    def shutdown(self):
        self.component_registry.unregister_handler(self._unlink_on_presentation_delete)
        self.component_registry.unregister_handler(self._unlink_on_stereotype_delete)
        self.component_registry.unregister_handler(self._unlink_on_extension_delete)
        self.component_registry.unregister_handler(self._disconnect_extension_end)

    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_presentation_delete(self, event):
        """
        Unlink the model element if no more presentations link to the `item`'s
        subject or the deleted item was the only item currently linked.
        """

        self.logger.debug("Handling IAssociationDeleteEvent")
        # self.logger.debug('Property is %s' % event.property.name)
        # self.logger.debug('Element is %s' % event.element)
        # self.logger.debug('Old value is %s' % event.old_value)

        if event.property is UML.Element.presentation:
            old_presentation = event.old_value
            if old_presentation and not event.element.presentation:
                event.element.unlink()

    def perform_unlink_for_instances(self, st, meta):

        self.logger.debug("Performing unlink for instances")
        # self.logger.debug('Stereotype is %s' % st)
        # self.logger.debug('Meta is %s' % meta)

        inst = UML.model.find_instances(self.element_factory, st)

        for i in list(inst):
            for e in i.extended:
                if not meta or isinstance(e, meta):
                    i.unlink()

    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_extension_delete(self, event):
        """
        Remove applied stereotypes when extension is deleted.
        """

        self.logger.debug("Handling IAssociationDeleteEvent")
        # self.logger.debug('Property is %s' % event.property.name)
        # self.logger.debug('Element is %s' % event.element)
        # self.logger.debug('Old value is %s' % event.old_value)

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
            meta = p.type and getattr(UML, p.type.name)
            self.perform_unlink_for_instances(st, meta)

    @component.adapter(IAssociationSetEvent)
    def _disconnect_extension_end(self, event):

        self.logger.debug("Handling IAssociationSetEvent")
        # self.logger.debug('Property is %s' % event.property.name)
        # self.logger.debug('Element is %s' % event.element)
        # self.logger.debug('Old value is %s' % event.old_value)

        if event.property is UML.ExtensionEnd.type and event.old_value:
            ext = event.element
            p = ext.opposite
            if not p:
                return
            st = event.old_value
            meta = getattr(UML, p.type.name)
            self.perform_unlink_for_instances(st, meta)

    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_stereotype_delete(self, event):
        """
        Remove applied stereotypes when stereotype is deleted.
        """

        self.logger.debug("Handling IAssociationDeleteEvent")
        # self.logger.debug('Property is %s' % event.property)
        # self.logger.debug('Element is %s' % event.element)
        # self.logger.debug('Old value is %s' % event.old_value)

        if event.property is UML.InstanceSpecification.classifier:
            if isinstance(event.old_value, UML.Stereotype):
                event.element.unlink()
