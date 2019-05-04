"""
TODO: Move component information (event handling, and other stuff done by
zope.component) to this service.

Maybe we should split the ComponentRegistry in a Dispatcher (register_handler,
unregister_handler, handle), a AdapterRegistry and a Subscription registry.
"""

from zope import component

from zope.interface import registry
from zope.interface import implementer

from gaphor.abc import Service
from gaphor.application import ComponentLookupError


class ZopeComponentRegistry(Service):
    """
    The ZopeComponentRegistry provides a subset of the
    ``zope.component.registry.Components`` interface. This part is mainly
    enough to get the work done and keeps stuff simpler.

    This service should not be called directly, but through more specific
    service such as Dispatcher and AdapterRegistry.
    """

    def __init__(self):
        self._comp = set()

    def init(self, app):
        self._components = registry.Components(
            name="component_registry", bases=(component.getGlobalSiteManager(),)
        )

    def shutdown(self):
        pass

    def get_service(self, name):
        """Obtain a service used by Gaphor by name.
        E.g. service("element_factory")
        """
        return self.get(Service, name)

    def register(self, component, name):
        self._comp.add((component, name))

    def unregister(self, component):
        self._comp = {(c, n) for c, n in self._comp if not c is component}

    def get(self, base, name):
        found = {(c, n) for c, n in self._comp if isinstance(c, base) and n == name}
        if len(found) > 1:
            raise ComponentLookupError(
                f"More than one component matches {base}+{name}: {found}"
            )
        if len(found) == 0:
            raise ComponentLookupError(
                f"Component with type {base} and name {name} is not registered"
            )
        return next(iter(found))[0]

    def all(self, base):
        return ((c, n) for c, n in self._comp if isinstance(c, base))

    # Wrap zope.component's Components methods

    def register_handler(self, factory, adapts=None):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emitted through the handle() method.
        """
        self._components.registerHandler(factory, adapts, event=False)

    def unregister_handler(self, factory=None, required=None):
        """
        Unregister a previously registered handler.
        """
        self._components.unregisterHandler(factory, required)

    def handle(self, *events):
        """
        Send event notifications to registered handlers.
        """
        list(map(self._components.handle, events))
