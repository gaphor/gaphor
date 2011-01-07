"""
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from zope import interface
from zope import component

from gaphor.misc.logger import Logger
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
    logger = Logger(name='EVENTDISPATCHER')

    component_registry = inject('component_registry')


    def __init__(self):
        pass


    def init(self, app=None):
        self.component_registry.register_handler(self._element_notify)


    def shutdown(self):
        self.logger.info('Shutting down')
        
        self.component_registry.unregister_handler(self._element_notify)
        
    @component.adapter(IElementEvent)
    def _element_notify(self, event):
        """
        Dispatch IElementEvent events to interested adapters registered
        by (class, event).
        """
        
        self.logger.info('Handling IElementEvent event')
        
        self.component_registry.handle(event.element, event)


# vim:sw=4:et:ai
