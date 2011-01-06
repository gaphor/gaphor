"""
"""

import gtk
from zope import interface, component

from gaphor.misc.logger import Logger
from gaphor.core import inject
from gaphor.interfaces import IService, IActionProvider
from gaphor.event import ServiceInitializedEvent, ActionExecuted

class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    interface.implements(IService)
    logger = Logger(name='ACTIONMANAGER')

    component_registry = inject('component_registry')

    def __init__(self):
        pass


    def init(self, app):
        self.ui_manager = gtk.UIManager()
        
        self.logger.info('Loading action provider services')
        
        for name, service in self.component_registry.get_utilities(IService):
            
            if IActionProvider.providedBy(service):
                
                self.logger.debug('Service is %s' % service)
                
                self.register_action_provider(service)

        self.component_registry.register_handler(self._service_initialized_handler)

    def shutdown(self):
        
        self.logger.info('Shutting down')
        
        self.component_registry.unregister_handler(self._service_initialized_handler)

    def execute(self, action_id, active=None):
        
        self.logger.info('Executing action')
        self.logger.debug('Action ID is %s' % action_id)
        
        a = self.get_action(action_id)
        if a:
            a.activate()
            self.component_registry.handle(ActionExecuted(action_id, a))
        else:
            self.logger.warning('Unknown action %s' % action_id)

    def update_actions(self):
        
        self.logger.info('Updating actions')
        
        self.ui_manager.ensure_update()

    def get_action(self, action_id):
        
        self.logger.info('Getting action')
        self.logger.debug('Action ID is %s' % action_id)
        
        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a: return a

    def register_action_provider(self, action_provider):
        
        self.logger.info('Registering action provider')
        self.logger.debug('Action provider is %s' % action_provider)
        
        action_provider = IActionProvider(action_provider)
        
        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            
            self.logger.debug('Registering actions for %s' % action_provider)
            
            assert action_provider.action_group
            
            self.ui_manager.insert_action_group(action_provider.action_group, -1)
            
            if action_provider.menu_xml:
            
                action_provider.__ui_merge_id = \
                        self.ui_manager.add_ui_from_string(action_provider.menu_xml)

    @component.adapter(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):
        
        self.logger.info('Handling ServiceInitializedEvent')
        self.logger.debug('Service is %s' % event.service)
        
        if IActionProvider.providedBy(event.service):
            
            self.logger.debug('Loading registered service %s' % event.service)
            
            self.register_action_provider(event.service)


# vim:sw=4:et:ai
