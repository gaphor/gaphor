"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

import logging
import functools
import pkg_resources

from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent
from gaphor.abc import Service

logger = logging.getLogger(__name__)


class NotInitializedError(Exception):
    pass


class ComponentLookupError(LookupError):
    pass


_ESSENTIAL_SERVICES = ["component_registry", "event_manager", "element_dispatcher"]


class _Application:
    """
    The Gaphor application is started from the Application instance. It behaves
    like a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered in the "component_registry" service.
    """

    def __init__(self):
        self._uninitialized_services = {}
        self._event_filter = None
        self._app = None
        self._essential_services = list(_ESSENTIAL_SERVICES)
        self.component_registry = None
        self.event_manager = None

    def init(self, services=None):
        """
        Initialize the application.
        """
        self.load_services(services)
        self.init_all_services()

    essential_services = property(
        lambda s: s._essential_services,
        doc="""
        Provide an ordered list of services that need to be loaded first.
        """,
    )

    def load_services(self, services=None):
        """
        Load services from resources.

        Service should provide an interface gaphor.abc.Service.
        """
        # Ensure essential services are always loaded.
        if services:
            for name in self.essential_services:
                if name not in services:
                    services.append(name)

        for ep in pkg_resources.iter_entry_points("gaphor.services"):
            cls = ep.load()
            if isinstance(cls, Service):
                raise NameError("Entry point %s doesn" "t provide Service" % ep.name)
            if not services or ep.name in services:
                logger.debug('found service entry point "%s"' % ep.name)
                srv = cls()
                self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        for name in self.essential_services:
            self.init_service(name)
        while self._uninitialized_services:
            self.init_service(next(iter(list(self._uninitialized_services.keys()))))

    def init_service(self, name):
        """
        Initialize a not yet initialized service.

        Raises ComponentLookupError if the service has not been found
        """
        try:
            srv = self._uninitialized_services.pop(name)
        except KeyError:
            raise ComponentLookupError(Service, name)
        else:
            logger.info("initializing service service.%s" % name)
            srv.init(self)

            # Bootstrap hassle:
            if name == "component_registry":
                self.component_registry = srv
            elif name == "event_manager":
                self.event_manager = srv

            self.component_registry.register(srv, name)
            if self.event_manager:
                self.event_manager.handle(ServiceInitializedEvent(name, srv))
            return srv

    distribution = property(
        lambda s: pkg_resources.get_distribution("gaphor"),
        doc="The PkgResources distribution for Gaphor",
    )

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("First call Application.init() to load services")

        try:
            return self.component_registry.get_service(name)
        except ComponentLookupError:
            return self.init_service(name)

    def shutdown(self):
        for srv, name in self.component_registry.all(Service):
            if name not in self.essential_services:
                self.shutdown_service(name)

        for name in reversed(self.essential_services):
            self.shutdown_service(name)

        self.component_registry = None

    def shutdown_service(self, name):
        srv = self.component_registry.get_service(name)
        self.event_manager.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister(srv)
        srv.shutdown()

    def run(self, model=None):
        """Start the GUI application.

        The file_manager service is used here to load a Gaphor model if one was
        specified on the command line."""

        from gi.repository import Gio, Gtk

        app = Gtk.Application(
            application_id="org.gaphor.Gaphor", flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self._app = app

        def app_startup(app):
            self.init()

        def app_activate(app):
            # Make sure gui is loaded ASAP.
            # This prevents menu items from appearing at unwanted places.
            main_window = self.get_service("main_window")
            main_window.open(app)
            app.add_window(main_window.window)

            file_manager = self.get_service("file_manager")

            if model:
                file_manager.load(model)
            else:
                file_manager.action_new()

        def app_shutdown(app):
            self.shutdown()

        def main_quit(action, param):
            # Perform the "luxe" quit version, as defined in MainWindow
            main_window = self.get_service("main_window")
            return main_window.quit()

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", main_quit)
        app.add_action(action)

        app.connect("startup", app_startup)
        app.connect("activate", app_activate)
        app.connect("shutdown", app_shutdown)
        app.run()

    def quit(self):
        """Quit the GUI application."""
        if self._app:
            self._app.quit()


# Make sure there is only one!
Application = _Application()


class inject:
    """
    Simple descriptor for dependency injection.
    This is technically a wrapper around Application.get_service().

    Usage::

    >>> class A:
    ...     element_factory = inject('element_factory')
    """

    def __init__(self, name):
        self._name = name

    def __get__(self, obj, class_=None):
        """
        Resolve a dependency, but only if we're called from an object instance.
        """
        if not obj:
            return self
        return Application.get_service(self._name)
