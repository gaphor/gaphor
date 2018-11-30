"""
"""

from builtins import object
from logging import getLogger
from zope import component

from gi.repository import Gtk
from zope.interface import implementer

from gaphor.core import inject
from gaphor.event import ServiceInitializedEvent, ActionExecuted
from gaphor.interfaces import IService, IActionProvider


@implementer(IService)
class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    logger = getLogger("ActionManager")

    component_registry = inject("component_registry")

    ui_manager = inject("ui_manager")

    def __init__(self):
        pass

    def init(self, app):
        self.logger.info("Loading action provider services")

        for name, service in self.component_registry.get_utilities(IActionProvider):
            self.logger.debug("Service is %s" % service)
            self.register_action_provider(service)

        self.component_registry.register_handler(self._service_initialized_handler)

    def shutdown(self):

        self.logger.info("Shutting down")

        self.component_registry.unregister_handler(self._service_initialized_handler)

    def execute(self, action_id, active=None):

        self.logger.debug("Executing action, action_id is %s" % action_id)

        a = self.get_action(action_id)
        if a:
            a.activate()
            self.component_registry.handle(ActionExecuted(action_id, a))
        else:
            self.logger.warning("Unknown action %s" % action_id)

    def update_actions(self):

        self.ui_manager.ensure_update()

    def get_action(self, action_id):

        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a:
                return a

    def register_action_provider(self, action_provider):

        self.logger.debug("Registering action provider %s" % action_provider)

        action_provider = IActionProvider(action_provider)

        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            assert action_provider.action_group
            self.ui_manager.insert_action_group(action_provider.action_group, -1)

            try:
                menu_xml = action_provider.menu_xml
            except AttributeError:
                pass
            else:
                action_provider.__ui_merge_id = self.ui_manager.add_ui_from_string(
                    menu_xml
                )

    @component.adapter(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):

        self.logger.debug("Handling ServiceInitializedEvent")
        self.logger.debug("Service is %s" % event.service)

        if IActionProvider.providedBy(event.service):

            self.logger.debug("Loading registered service %s" % event.service)

            self.register_action_provider(event.service)


@implementer(IService)
class UIManager(Gtk.UIManager):
    """
    Service version of Gtk.UIManager.
    """

    def init(self, app=None):
        pass

    def shutdown(self):
        pass


# vim:sw=4:et:ai
