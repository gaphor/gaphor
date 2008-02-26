"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from zope import interface
from zope import component
from gaphor import UML
from gaphor.UML.interfaces import IElementDeleteEvent
from gaphor.interfaces import IService


class SanitizerService(object):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """
    interface.implements(IService)

    def __init__(self):
        pass

    def init(self, app):
        self._app = app
        app.register_handler(self._unlink_on_presentation_delete)

    def shutdown(self):
        self._app.unregister_handler(self._unlink_on_presentation_delete)
        
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


# vim:sw=4:et:ai
