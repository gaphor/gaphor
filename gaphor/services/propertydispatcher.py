"""
"""

from zope import interface, component

from gaphor.misc.logger import Logger
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementChangeEvent


class PropertyDispatcher(object):
    """
    The Propery Dispatcher allows classes to register on events originated
    by a specific element property, instead of the event type.

    This makes it easier for (for example) items to register on events from
    a specific class, rather than just AssociationChangeEvents, which could
    originate on a whole lot of classes.
    """

    interface.implements(IService)
    logger = Logger(name='PROPERTYDISPATCHER')

    def __init__(self):
        # Handlers is a dict of sets
        self._handlers = {}

    def init(self, app):
        
        self.logger.info('Starting')
        
        self._app = app
        app.register_handler(self.on_element_change_event)

    def shutdown(self):
        
        self.logger.info('Shutting down')
        
        self._app.unregister_handler(self.on_element_change_event)
        self._app = None

    def register_handler(self, property, handler, exact=False):
        
        self.logger.info('Registring handler')
        self.logger.debug('Property is %s' % property)
        self.logger.debug('Handler is %s' % handler)
        
        try:
            self._handlers[property].add(handler)
        except KeyError:
            self._handlers[property] = set([handler])

    def unregister_handler(self, property, handler):
        
        self.logger.info('Unregistering handler')
        self.logger.debug('Property is %s' % property)
        self.logger.debug('Handler is %s' % handler)
        
        s = self._handlers.get(property)
        if s:
            s.discard(handler)

    @component.adapter(IElementChangeEvent)
    def on_element_change_event(self, event):
        
        self.logger.info('Handling IElementChangeEvent')
        
        property = event.property
        
        self.logger.debug('Property is %s' % property)

        s = self._handlers.get(property)
        if not s:
            return
        for handler in s:
            try:
                handler(event)
            except Exception, e:
                log.error('problem executing handler %s' % handler, e)


# vim:sw=4:et:ai
