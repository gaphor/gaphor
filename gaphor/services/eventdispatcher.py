"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from zope import interface
from zope import component
from gaphor import UML
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementEvent


class EventDispatcher(object):
    """
    Do slightly more complex event dispatching.

    This service should take over the dispatching capabilities of Application.
    """
    interface.implements(IService)

#    component_registry = inject('component_registry')


    def __init__(self):
        pass


    def init(self, app=None):
        self._app = app
        app.register_handler(self._element_notify)


    def shutdown(self):
        self._app.unregister_handler(self._element_notify)
        

    @component.adapter(IElementEvent)
    def _element_notify(self, event):
        """
        Dispatch IElementEvent events to interested adapters registered
        by (class, event).
        """
        if self._app:
            self._app.handle(event.element, event)


#    def register_handler(self, factory, adapts=None):
#        """
#        Register a handler. Handlers are triggered (executed) when specific
#        events are emitted through the handle() method.
#        """
#        self.component_registry.register_handler(factory, adapts)


#    def unregister_handler(self, factory=None, required=None):
#        """
#        Unregister a previously registered handler.
#        """
#        self.component_registry.unregister_handler(factory, required)


#    def fire(self, *events):
#        """
#        Send out one or more events.
#        """
#        self.component_registry.handle(events)


# vim:sw=4:et:ai
