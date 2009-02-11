"""
"""

from zope import interface, component
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementEvent


class ClassBasedDispatcher(object):
    """
    The Class based Dispatcher allows classes to register on events originated
    by a specific element type, instead of the event type.

    This makes it easier for (for example) items to register on events from
    a specific class, rather than just AssociationChangeEvents, which could
    originate on a whole lot of classes.
    """

    interface.implements(IService)

    def __init__(self):
        # Handlers is a dict of sets
        self._handlers = {}

    def init(self, app):
        self._app = app
        app.register_handler(self.on_element_event)

    def shutdown(self):
        self._app.unregister_handler(self.on_element_event)
        self._app = None

    def register_handler(self, type, handler, exact=False):
        try:
            self._handlers[type].add(handler)
        except KeyError:
            self._handlers[type] = set([handler])


    def unregister_handler(self, type, handler):
        s = self._handlers.get(type)
        if s:
            s.discard(handler)


    @component.adapter(IElementEvent)
    def on_element_event(self, event):
        element = event.element
        # Cache this?
        for c in type(element).__mro__:
            # Find registered items for this element
            s = self._handlers.get(c)
            if not s:
                continue
            for handler in s:
                try:
                    handler(event)
                except Exception, e:
                    log.error('problem executing handler %s' % handler, e)


# vim:sw=4:et:ai
