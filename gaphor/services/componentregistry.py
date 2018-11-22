"""
TODO: Move component information (event handling, and other stuff done by
zope.component) to this service.

Maybe we should split the ComponentRegistry in a Dispatcher (register_handler,
unregister_handler, handle), a AdapterRegistry and a Subscription registry.
"""

from builtins import map
from builtins import object
from zope import component

from zope.interface import registry
from zope.interface import implementer

from gaphor.interfaces import IService, IEventFilter


@implementer(IService)
class ZopeComponentRegistry(object):
    """
    The ZopeComponentRegistry provides a subset of the
    ``zope.component.registry.Components`` interface. This part is mainly
    enough to get the work done and keeps stuff simpler.

    This service should not be called directly, but through more specific
    service such as Dispatcher and AdapterRegistry.
    """

    def __init__(self):
        pass

    def init(self, app):
        self._components = registry.Components(
                               name='component_registry',
                               bases=(component.getGlobalSiteManager(),))

        # Make sure component.handle() and query methods works.
        # TODO: eventually all queries should be done through the Application
        # instance.
        # Used in collection.py, transaction.py, diagramtoolbox.py:
        component.handle = self.handle
        #component.getMultiAdapter = self._components.getMultiAdapter
        # Used all over the place:
        component.queryMultiAdapter = self._components.queryMultiAdapter
        #component.getAdapter = self._components.getAdapter
        #component.queryAdapter = self._components.queryAdapter
        # Used in propertyeditor.py:
        component.getAdapters = self._components.getAdapters
        #component.getUtility = self._components.getUtility
        # Used in test cases (test_application.py)
        component.queryUtility = self._components.queryUtility
        #component.getUtilitiesFor = self._components.getUtilitiesFor


    def shutdown(self):
        pass


    def get_service(self, name):
        return self.get_utility(IService, name)


    # Wrap zope.component's Components methods

    def register_utility(self, component=None, provided=None, name=''):
        """
        Register a component (e.g. Service)
        """
        self._components.registerUtility(component, provided, name)

    def unregister_utility(self, component=None, provided=None, name=''):
        """
        Unregister a component (e.g. Service)
        """
        self._components.unregisterUtility(component, provided, name)

    def get_utility(self, provided, name=''):
        """
        Get a component from the registry.
        zope.component.ComponentLookupError is thrown if no such component
        exists.
        """
        return self._components.getUtility(provided, name)

    def get_utilities(self, provided):
        """
        Iterate over all components that provide a certain interface.
        """
        for name, utility in self._components.getUtilitiesFor(provided):
            yield name, utility

    def register_adapter(self, factory, adapts=None, provides=None, name=''):
        """
        Register an adapter (factory) that adapts objects to a specific
        interface. A name can be used to distinguish between different adapters
        that adapt to the same interfaces.
        """
        self._components.registerAdapter(factory, adapts, provides,
                              name, event=False)

    def unregister_adapter(self, factory=None,
                           required=None, provided=None, name=u''):
        """
        Unregister a previously registered adapter.
        """
        self._components.unregisterAdapter(factory,
                              required, provided, name)

    def get_adapter(self, objects, interface):
        """
        Obtain an adapter that adheres to a specific interface. Objects can be either
        a single object or a tuple of objects (multi adapter).

        If nothing is found `None` is returned.
        """
        if isinstance(objects, (list, tuple)):
            return self._components.queryMultiAdapter(objects, interface)
        return self._components.queryAdapter(objects, interface)

    def register_subscription_adapter(self, factory, adapts=None, provides=None):
        """
        Register a subscription adapter. See registerAdapter().
        """
        self._components.registerSubscriptionAdapter(factory, adapts,
                              provides, event=False)

    def unregister_subscription_adapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered subscription adapter.
        """
        self._components.unregisterSubscriptionAdapter(factory,
                              required, provided, name)

    def subscribers(self, objects, interface):
        return self._components.subscribers(objects, interface)

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

    def _filter(self, objects):
        filtered = list(objects)
        for o in objects:
            for adapter in self._components.subscribers(objects, IEventFilter):
                if adapter.filter():
                    # event is blocked
                    filtered.remove(o)
                    break
        return filtered

    def handle(self, *events):
        """
        Send event notifications to registered handlers.
        """
        objects = self._filter(events)
        if objects:
            list(map(self._components.handle, events))


# vim:sw=4:et:ai
