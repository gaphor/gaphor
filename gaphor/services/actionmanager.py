"""
"""

import gtk
from zope import interface, component
from gaphor.core import inject
from gaphor.interfaces import IService, IActionProvider
from gaphor.event import ServiceInitializedEvent
from gaphor.misc.action import ActionPool

class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    interface.implements(IService)

    def __init__(self):
        pass

    def init(self, app):
        self.ui_manager = gtk.UIManager()
        component.provideHandler(self._service_initialized_handler)

    def shutdown(self):
        pass

    def execute(self, action_id, active=None):
        a = self.get_action(action_id)
        if a:
            a.activate()
        else:
            log.warning('Unknown action: %s' % action_id)

    def update_actions(self):
        self.ui_manager.ensure_update()

    def get_action(self, action_id):
        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a: return a

    def register_action_provider(self, action_provider, priority=-1):
        log.debug('Registring actions for %s' % str(action_provider))
        action_provider = IActionProvider(action_provider)
        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            
            if action_provider.menu_xml:
                action_provider.__ui_merge_id = \
                        self.ui_manager.add_ui_from_string(action_provider.menu_xml)
            self.ui_manager.insert_action_group(action_provider.action_group, priority)

    @component.adapter(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):
        if IActionProvider.providedBy(event.service):
            self.register_action_provider(event.service)
        # Only start registring already registered services once the GUI
        # is in order (e.i. menu structure is correctly set up)
        if event.name == 'gui_manager':
            for name, service in component.getUtilitiesFor(IService):
                if IActionProvider.providedBy(service):
                    self.register_action_provider(service)

# vim:sw=4:et:ai
