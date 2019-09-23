"""
"""

from typing import Set
import logging

from gi.repository import GLib, Gio, Gtk

from gaphor.core import event_handler, action, toggle_action, radio_action
from gaphor.event import ServiceInitializedEvent, ActionExecuted
from gaphor.abc import Service, ActionProvider

logger = logging.getLogger(__name__)


class ActionManager(Service):
    """
    This service is responsible for maintaining actions.
    """

    menubar_path = "/mainwindow"
    toolbar_path = "/mainwindow-toolbar"

    menu_skeleton_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary" />
            <separator />
            <menu action="file-export" />
            <menu action="file-import" />
            <separator />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
            <separator />
          </menu>
          <menu action="edit">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="diagram">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="tools">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="help">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
            <placeholder name="left" />
            <separator expand="true" />
            <placeholder name="right" />
        </toolbar>
      </ui>
    """

    def __init__(self, event_manager, component_registry):
        self.event_manager = event_manager
        self.component_registry = component_registry

        self.ui_manager = Gtk.UIManager()
        self.ui_manager.add_ui_from_string(self.menu_skeleton_xml)

        logger.info("Loading action provider services")

        for service, name in self.component_registry.all(ActionProvider):
            logger.debug(f"Service is {service}")
            self.register_action_provider(service)

        self.event_manager.subscribe(self._service_initialized_handler)

    def shutdown(self):
        self.event_manager.unsubscribe(self._service_initialized_handler)

    def execute(self, action_id, active=None):

        logger.debug(f"Executing action, action_id is {action_id}")

        a = self.get_action(action_id)
        if a:
            a.activate()
            self.event_manager.handle(ActionExecuted(action_id, a))
        else:
            logger.warning(f"Unknown action {action_id}")

    def update_actions(self):

        self.ui_manager.ensure_update()

    def get_action(self, action_id):

        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a:
                return a

    def register_action_provider(self, action_provider):

        logger.debug(f"Registering action provider {action_provider}")

        # Old code, to be deprecated
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

    def unregister_action_provider(self, action_provider):

        # Old code, to be deprecated
        try:
            # Check if the action provider is registered
            action_provider.__ui_merge_id
        except AttributeError:
            pass
        else:
            self.ui_manager.remove_ui(action_provider.__ui_merge_id)
            self.ui_manager.remove_action_group(action_provider.action_group)
            del action_provider.__ui_merge_id

    @event_handler(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):

        logger.debug("Handling ServiceInitializedEvent")
        logger.debug(f"Service is {event.service}")

        if isinstance(event.service, ActionProvider):

            logger.debug(f"Loading registered service {event.service}")

            self.register_action_provider(event.service)

    # UIManager methods (deprecated):

    def get_widget(self, path):
        return self.ui_manager.get_widget(path)

    def get_accel_group(self):
        return self.ui_manager.get_accel_group()

    # GIO ActionGroup methods:

    def apply_application_actions(self, gtk_app):
        return self.action_group_for_scope(gtk_app, "app")

    def window_action_group(self):
        return self.action_group_for_scope(Gio.SimpleActionGroup.new(), "win")

    def action_group_for_scope(self, action_group, scope):
        for provider, _name in self.component_registry.all(ActionProvider):
            provider_class = type(provider)
            for attrname in dir(provider_class):
                method = getattr(provider_class, attrname)
                act = getattr(method, "__action__", None)
                if not act or act.scope != scope:
                    continue

                if isinstance(act, radio_action):
                    a = Gio.SimpleAction.new_stateful(
                        act.name, None, GLib.Variant.new_int16(act.active)
                    )
                    a.connect(
                        "change-state", _radio_action_activate, provider, attrname
                    )
                elif isinstance(act, toggle_action):
                    a = Gio.SimpleAction.new_stateful(
                        act.name, None, GLib.Variant.new_boolean(act.active)
                    )
                    a.connect(
                        "change-state", _toggle_action_activate, provider, attrname
                    )
                elif isinstance(act, action):
                    a = Gio.SimpleAction.new(act.name, None)
                    a.connect("activate", _action_activate, provider, attrname)
                else:
                    raise ValueError(f"Action is not of a known action type ({act})")
                action_group.add_action(a)
        return action_group


def _action_activate(_action, _param, obj, name):
    method = getattr(obj, name)
    method()


def _toggle_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_boolean())


def _radio_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_int16())
