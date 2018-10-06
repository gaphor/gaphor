"""
"""

from builtins import object
from zope import interface, component

from logging import getLogger
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementChangeEvent, IModelFactoryEvent
from gaphor import UML
from gaphor.UML.interfaces import IAssociationSetEvent,\
                                  IAssociationAddEvent,\
                                  IAssociationDeleteEvent

class EventWatcher(object):
    """
    A helper for easy registering and unregistering event handlers.
    """

    element_dispatcher = inject('element_dispatcher')
    logger = getLogger('EventWatcher')

    def __init__(self, element, default_handler=None):
        super(EventWatcher, self).__init__()
        self.element = element
        self.default_handler = default_handler
        self._watched_paths = dict()

    def watch(self, path, handler=None):
        """
        Watch a certain path of elements starting with the DiagramItem.
        The handler is optional and will default the default provided at
        construction time.
        
        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        
        #self.logger.info('Watching element path')
        #self.logger.debug('Path is %s' % path)
        #self.logger.debug('Handler is %s' % handler)
        
        if handler:
            self._watched_paths[path] = handler
        elif self.default_handler:
            self._watched_paths[path] = self.default_handler
        else:
            raise ValueError('No handler provided for path ' + path)
        return self


    def register_handlers(self):
        
        #self.logger.info('Registering handlers')
        
        dispatcher = self.element_dispatcher
        element = self.element
        
        for path, handler in self._watched_paths.items():
            
            #self.logger.debug('Path is %s' % path)
            #self.logger.debug('Handler is %s' % handler)
            
            dispatcher.register_handler(handler, element, path)


    def unregister_handlers(self, *args):
        """
        Unregister handlers. Extra arguments are ignored (makes connecting to
        destroy signals much easier though).
        """
        
        #self.logger.info('Unregistering handlers')
        
        dispatcher = self.element_dispatcher
        
        for path, handler in self._watched_paths.items():
            
            #self.logger.debug('Path is %s' % path)
            #self.logger.debug('Handler is %s' % handler)
            
            dispatcher.unregister_handler(handler)

class ElementDispatcher(object):
    """
    The Element based Dispatcher allows handlers to receive only events
    related to certain elements. Those elements should be registered to. Also
    a path should be provided, that is used to find those changes. 

    The handlers are registered on their property attribute. This avoids
    subclass lookups and is pretty specific. As a result this dispatcher is
    tailored for dispatching events from the data model (IElementChangeEvent)

    For example: if you're a TransitionItem (UML.Presentation instance) and
    you're interested in the value of the guard attribute of the model element
    that's represented by this item (gaphor.UML.Transition), you can register
    a handler like this::

      dispatcher.register_handler(element,
              'guard.specification<LiteralSpecification>.value', self._handler)

    Note the '<' and '>'. This is because guard references ValueSpecification,
    which does not have a value attribute. Therefore the default reference type
    is overruled in favour of the LiteralSpecification.

    This dispatcher keeps track of the kind of events that are dispatched. The
    dispatcher table is updated accordingly (so the right handlers are fired
    every time).
    """

    interface.implements(IService)
    logger = getLogger('ElementDispatcher')

    component_registry = inject('component_registry')

    def __init__(self):
        # Table used to fire events:
        # (event.element, event.property): { handler: set(path, ..), ..}
        self._handlers = dict()

        # Fast resolution when handlers are disconnected
        # handler: [(element, property), ..]
        self._reverse = dict()


    def init(self, app):
        self.component_registry.register_handler(self.on_model_loaded)
        self.component_registry.register_handler(self.on_element_change_event)


    def shutdown(self):
        self.component_registry.unregister_handler(self.on_element_change_event)
        self.component_registry.unregister_handler(self.on_model_loaded)


    def _path_to_properties(self, element, path):
        """
        Given a start element and a path, return a tuple of UML properties
        (association, attribute, etc.) representing the path.

        >>> from gaphor import UML
        >>> dispatcher = ElementDispatcher()
        >>> sorted(map(str, dispatcher._path_to_properties(UML.Class(),
        ...         'ownedOperation.parameter.name'))) # doctest: +NORMALIZE_WHITESPACE
        ['<association ownedOperation: Operation[0..*] <>-> class_>',
        "<attribute name: <type 'str'>[0..1] = None>",
        "<derived parameter:
            '<association formalParameter: Parameter[0..*] <>-> ownerFormalParam>',
            '<association returnResult: Parameter[0..*] <>-> ownerReturnParam>'>"]

        Should also work for elements that use subtypes of a certain class:

        >>> sorted(map(str, dispatcher._path_to_properties(UML.Transition(),
        ...         'guard.specification'))) # doctest: +NORMALIZE_WHITESPACE
        ['<association guard: Constraint[0..1]>',
         "<attribute specification: <type 'str'>[0..1] = None>"]
        """
        c = type(element)
        tpath = []
        for attr in path.split('.'):
            cname = ''
            if '<' in attr:
                assert attr.endswith('>'), '"%s" should end with ">"' % attr
                attr, cname = attr[:-1].split('<')
            prop = getattr(c, attr)
            tpath.append(prop)
            if cname:
                c = getattr(UML, cname)
                assert issubclass(c, prop.type), '%s should be a subclass of %s' % (c, prop.type)
            else:
                c = prop.type
        return tuple(tpath)


    def _add_handlers(self, element, props, handler):
        """
        Provided an element and a path of properties (props), register the
        handler for each property.
        """
        property, remainder = props[0], props[1:]
        key = (element, property)
        
        # Register key
        try:
            handlers = self._handlers[key]
        except KeyError:
            handlers = dict()
            self._handlers[key] = handlers

        # Register handler and it's remaining paths
        try:
            remainders = handlers[handler]
        except KeyError:
            remainders = handlers[handler] = set()
        if remainder:
            remainders.add(remainder)

        # Also add them to the reverse table, easing disconnecting
        try:
            reverse = self._reverse[handler]       
        except KeyError:
            reverse = []
            self._reverse[handler] = reverse

        reverse.append(key)

        # Apply remaining path
        if remainder:
            if property.upper > 1:
                for e in property._get(element):
                    self._add_handlers(e, remainder, handler)
            else:
                e = property._get(element)
                if e and remainder:
                    self._add_handlers(e, remainder, handler)


    def _remove_handlers(self, element, property, handler):
        """
        Remove the handler of the path of elements.
        """
        key = element, property
        handlers = self._handlers.get(key)
        if not handlers:
            return

        if property.upper > 1:
            for remainder in handlers.get(handler, ()):
                for e in property._get(element):
                    #log.debug(' Remove handler %s for key %s, element %s' % (handler, str(remainder[0].name), e))
                    self._remove_handlers(e, remainder[0], handler)
        else:
            for remainder in handlers.get(handler, ()):
                e = property._get(element)
                if e:
                    #log.debug('*Remove handler %s for key %s, element %s' % (handler, str(remainder[0].name), e))
                    self._remove_handlers(e, remainder[0], handler)
        try:
            del handlers[handler]
        except KeyError:
            self.logger.warning('Handler %s is not registered for %s.%s' % (handler, element, property))

        if not handlers:
            del self._handlers[key]


    def register_handler(self, handler, element, path):
        
        #self.logger.info('Registering handler')
        #self.logger.debug('Handler is %s' % handler)
        #self.logger.debug('Element is %s' % element)
        #self.logger.debug('Path is %s' % path)
        
        props = self._path_to_properties(element, path)
        self._add_handlers(element, props, handler)


    def unregister_handler(self, handler):
        """
        Unregister a handler from the registy.
        """
        
        #self.logger.info('Unregistering handler')
        #self.logger.debug('Handler is %s' % handler)
        
        try:
            reverse = reversed(self._reverse[handler])
        except KeyError:
            return

        for key in reverse:
            try:
                handlers = self._handlers[key]
            except KeyError:
                pass
            else:
                try:
                    del handlers[handler]
                except KeyError:
                    pass
                if not handlers:
                    del self._handlers[key]
        del self._reverse[handler]


    @component.adapter(IElementChangeEvent)
    def on_element_change_event(self, event):
        
        #self.logger.info('Handling IElementChangeEvent')
        #self.logger.debug('Element is %s' % event.element)
        #self.logger.debug('Property is %s' % event.property)
        
        handlers = self._handlers.get((event.element, event.property))
        if handlers:
            #log.debug('')
            #log.debug('Element change for %s %s [%s]' % (str(type(event)), event.element, event.property))
            #if hasattr(event, 'old_value'):
            #    log.debug('    old value: %s' % (event.old_value))
            #if hasattr(event, 'new_value'):
            #    log.debug('    new value: %s' % (event.new_value))
            for handler in handlers.keys():
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error('Problem executing handler %s' % handler)
                    self.logger.error(e)
        
            # Handle add/removal of handlers based on the kind of event
            # Filter out handlers that have no remaining properties
            if IAssociationSetEvent.providedBy(event):
                for handler, remainders in handlers.items():
                    if remainders and event.old_value:
                        for remainder in remainders:
                            self._remove_handlers(event.old_value, remainder[0], handler)
                    if remainders and event.new_value:
                        for remainder in remainders:
                            self._add_handlers(event.new_value, remainder, handler)
            elif IAssociationAddEvent.providedBy(event):
                for handler, remainders in handlers.items():
                    for remainder in remainders:
                        self._add_handlers(event.new_value, remainder, handler)
            elif IAssociationDeleteEvent.providedBy(event):
                for handler, remainders in handlers.items():
                    for remainder in remainders:
                        self._remove_handlers(event.old_value, remainder[0], handler)


    @component.adapter(IModelFactoryEvent)
    def on_model_loaded(self, event):
        
        #self.logger.info('Handling IModelFactoryEvent')
        #self.logger.debug('Event is %s' % event)
        
        for key, value in list(self._handlers.items()):
            for h, remainders in list(value.items()):
                for remainder in remainders:
                    self._add_handlers(key[0], (key[1],) + remainder, h)
#        for h in self._reverse.iterkeys():
#            h(None)

# vim:sw=4:et:ai
