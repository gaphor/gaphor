"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from zope import interface
from zope import component
from gaphor import UML
from gaphor.UML.interfaces import IAssociationDeleteEvent, IAssociationSetEvent
from gaphor.interfaces import IService
from gaphor.core import inject
from gaphor.diagram import items

class SanitizerService(object):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """
    interface.implements(IService)

    element_factory = inject('element_factory')
    property_dispatcher = inject('property_dispatcher')

    def __init__(self):
        pass

    def init(self, app):
        self._app = app
        app.register_handler(self._unlink_on_presentation_delete)
        app.register_handler(self._unlink_on_stereotype_delete)
        app.register_handler(self._unlink_on_extension_delete)
        app.register_handler(self._disconnect_extension_end)

    def shutdown(self):
        self._app.unregister_handler(self._unlink_on_presentation_delete)
        self._app.unregister_handler(self._unlink_on_stereotype_delete)
        self._app.unregister_handler(self._unlink_on_extension_delete)
        self._app.unregister_handler(self._disconnect_extension_end)
        

    @component.adapter(IAssociationDeleteEvent)
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
        inst = UML.model.find_instances(self.element_factory, st)
        log.debug('Unlinking instances of stereotype %s' % st)
        for i in list(inst):
            for e in i.extended:
                if isinstance(e, meta):
                    i.unlink()


    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_extension_delete(self, event):
        """
        Remove applied stereotypes when extension is deleted.
        """
        if isinstance(event.element, UML.Extension) and \
                event.property is UML.Association.memberEnd and \
                event.element.memberEnd:
            p = event.element.memberEnd[0]
            ext = event.old_value
            if isinstance(p, UML.ExtensionEnd):
                p, ext = ext, p
            st = ext.type
            meta = getattr(UML, p.type.name)
            self.perform_unlink_for_instances(st, meta)


    @component.adapter(IAssociationSetEvent)
    def _disconnect_extension_end(self, event):
        #print event.property, event.element
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
        if event.property is UML.InstanceSpecification.classifier:
            if isinstance(event.old_value, UML.Stereotype):
                log.debug('Unlinking instances of stereotype %s' % event.old_value)
                event.element.unlink()


# vim:sw=4:et:ai
