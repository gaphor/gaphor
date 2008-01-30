"""
"""

import gtk
from zope import interface, component
from gaphor.core import inject
from gaphor.interfaces import IService, IActionProvider
from gaphor.event import ServiceInitializedEvent, ActionExecuted


class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    interface.implements(IService)

    def __init__(self):
        pass

    def init(self, app):
        self._app = app
        self.ui_manager = gtk.UIManager()
        log.info('Loading not yet registered action provider services')
        for name, service in component.getUtilitiesFor(IService):
            if IActionProvider.providedBy(service):
                log.debug('Loading already registered service %s' % str(service))
                self.register_action_provider(service)

        app.register_handler(self._service_initialized_handler)

    def shutdown(self):
        self._app.unregister_handler(self._service_initialized_handler)

    def execute(self, action_id, active=None):
        a = self.get_action(action_id)
        if a:
            a.activate()
            self._app.handle(ActionExecuted(action_id, a))
        else:
            log.warning('Unknown action: %s' % action_id)

    def update_actions(self):
        self.ui_manager.ensure_update()

    def get_action(self, action_id):
        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a: return a

    def register_action_provider(self, action_provider):
        action_provider = IActionProvider(action_provider)
        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            log.debug('Registering actions for %s' % str(action_provider))
            
            assert action_provider.action_group
            self.ui_manager.insert_action_group(action_provider.action_group, -1)
            if action_provider.menu_xml:
                action_provider.__ui_merge_id = \
                        self.ui_manager.add_ui_from_string(action_provider.menu_xml)

    @component.adapter(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):
        if IActionProvider.providedBy(event.service):
            log.debug('Loading registered service %s' % str(event.service))
            self.register_action_provider(event.service)


# vim:sw=4:et:ai
