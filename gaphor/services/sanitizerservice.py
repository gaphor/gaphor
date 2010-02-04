"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from zope import interface
from zope import component
from gaphor import UML
from gaphor.UML.interfaces import IElementDeleteEvent
from gaphor.interfaces import IService
from gaphor.core import inject


class SanitizerService(object):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """
    interface.implements(IService)

    element_factory = inject('element_factory')

    def __init__(self):
        pass

    def init(self, app):
        self._app = app
        app.register_handler(self._unlink_on_presentation_delete)
        app.register_handler(self._unlink_on_stereotype_attribute_delete)
        app.register_handler(self._unlink_on_stereotype_delete)
        app.register_handler(self._unlink_on_extension_delete)


    def shutdown(self):
        self._app.unregister_handler(self._unlink_on_presentation_delete)
        self._app.unregister_handler(self._unlink_on_stereotype_attribute_delete)
        self._app.unregister_handler(self._unlink_on_stereotype_delete)
        self._app.unregister_handler(self._unlink_on_extension_delete)
        

    @component.adapter(UML.Presentation, IElementDeleteEvent)
    def _unlink_on_presentation_delete(self, item, event):
        """
        Unlink the model element if no more presentations link to the `item`'s
        subject or the to-be-deleted item is the only item currently linked.
        """
        subject = item.subject
        if subject:
            presentation = subject.presentation
            if not presentation or \
                    (len(presentation) == 1 and presentation[0] is item):
                subject.unlink()


    @component.adapter(UML.Extension, IElementDeleteEvent)
    def _unlink_on_extension_delete(self, ext, event):
        """
        Remove applied stereotypes when extension is deleted.
        """
        for end in ext.memberEnd:
            st = end.type
            if isinstance(st, UML.Stereotype):
                instances = UML.model.find_instances(self.element_factory, st)
                for obj in list(instances):
                    UML.model.remove_stereotype(obj.extended[0], obj.classifier[0])


    @component.adapter(UML.Stereotype, IElementDeleteEvent)
    def _unlink_on_stereotype_delete(self, st, event):
        """
        Remove applied stereotypes when stereotype is deleted.
        """
        instances = UML.model.find_instances(self.element_factory, st)
        for obj in list(instances):
            e = obj.extended[0]
            c = obj.classifier[0]
            UML.model.remove_stereotype(e, c)


    @component.adapter(UML.Property, IElementDeleteEvent)
    def _unlink_on_stereotype_attribute_delete(self, st_attr, event):
        """
        Remove slots of instance specification (created due to applied
        stereotype) if stereotype's attribute is deleted.
        """
        if st_attr is not None and st_attr.class_ is not None \
                and st_attr.class_.isKindOf(UML.Stereotype):

            st = st_attr.class_
            instances = UML.model.find_instances(self.element_factory, st)
            for obj in list(instances):
                for slot in obj.slot:
                    if slot.definingFeature == st_attr:
                        del obj.slot[slot]
                        slot.unlink()

# vim:sw=4:et:ai
