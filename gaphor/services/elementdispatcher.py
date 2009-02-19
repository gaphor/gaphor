"""
"""

from zope import interface, component
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementChangeEvent, IModelFactoryEvent
from gaphor import UML
from gaphor.UML.interfaces import IAssociationSetEvent, IAssociationAddEvent, IAssociationDeleteEvent

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

    def __init__(self):
        # Table used to fire events:
        # (event.element, event.property): { handler: path, ..}
        self._handlers = dict()

        # Fast resolution when handlers are disconnected
        # handler: [(element, property), ..]
        self._reverse = dict()


    def init(self, app):
        self._app = app
        app.register_handler(self.on_model_loaded)
        app.register_handler(self.on_element_change_event)


    def shutdown(self):
        self._app.unregister_handler(self.on_element_change_event)
        self._app.unregister_handler(self.on_model_loaded)
        self._app = None


    def _path_to_properties(self, element, path):
        """
        Given a start element and a path, return a tuple of UML properties
        (association, attribute, etc.) representing the path.

        >>> from gaphor import UML
        >>> dispatcher = ElementDispatcher()
        >>> map(str, dispatcher._path_to_properties(UML.Class(),
        ...         'ownedOperation.parameter.name')) # doctest: +NORMALIZE_WHITESPACE
        ['<association ownedOperation: Operation[0..*] <>-> class_>',
        "<derivedunion parameter:
            '<association returnResult: Parameter[0..*] <>-> ownerReturnParam>',
            '<association formalParameter: Parameter[0..*] <>-> ownerFormalParam>'>",
        "<attribute name: <type 'str'>[0..1] = None>"]

        Should also work for elements that use subtypes of a certain class:

        >>> map(str, dispatcher._path_to_properties(UML.Transition(),
        ...         'guard.specification<LiteralSpecification>.value')) # doctest: +NORMALIZE_WHITESPACE
        ['<association guard: Constraint[0..1]>',
         '<association specification: ValueSpecification[1]>',
         "<attribute value: <type 'object'>[0..1] = None>"]
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
        try:
            handlers = self._handlers[key]
        except KeyError:
            handlers = dict()
            self._handlers[key] = handlers

        if handlers.get(handler):
            print 'overwrite:', map(str,handlers.get(handler)), map(str,remainder)
        try:
            remainders = handlers[handler]
        except KeyError:
            remainders = handlers[handler] = set()
        if remainder:
            remainders.add(remainder)

        try:
            reverse = self._reverse[handler]       
        except KeyError:
            reverse = []
            self._reverse[handler] = reverse

        reverse.append(key)

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

        for h, remainders in handlers.items():
            if h is handler:
                for remainder in remainders:
                    if property.upper > 1:
                        for e in property._get(element):
                            self._remove_handlers(e, remainder[0], handler)
                    else:
                        e = property._get(element)
                        if e:
                            self._remove_handlers(e, remainder[0], handler)
            del handlers[h]
        if not handlers:
            del self._handlers[key]


    def register_handler(self, handler, element, path):
        props = self._path_to_properties(element, path)
        self._add_handlers(element, props, handler)


    def unregister_handler(self, handler):
        """
        Unregister a handler from the registy.
        """
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
        handlers = self._handlers.get((event.element, event.property))
        if handlers:
            for handler in handlers.iterkeys():
                try:
                    handler(event)
                except Exception, e:
                    log.error('problem executing handler %s' % handler, e)
        
            # Handle add/removal of handlers based on the kind of event
            # Filter out handlers that have no remaining properties
            if IAssociationSetEvent.providedBy(event):
                for handler, remainders in handlers.iteritems():
                    if remainders and event.old_value:
                        for remainder in remainders:
                            self._remove_handlers(event.old_value, remainder[0], handler)
                    if remainders and event.new_value:
                        for remainder in remainders:
                            self._add_handlers(event.new_value, remainder, handler)
            elif IAssociationAddEvent.providedBy(event):
                for handler, remainders in handlers.iteritems():
                    for remainder in remainders:
                        self._add_handlers(event.new_value, remainder, handler)
            elif IAssociationDeleteEvent.providedBy(event):
                for handler, remainders in handlers.iteritems():
                    for remainder in remainders:
                        self._remove_handlers(event.old_value, remainder[0], handler)

    @component.adapter(IModelFactoryEvent)
    def on_model_loaded(self, event):
        for key, value in self._handlers.items():
            for h, remainders in value.items():
                for remainder in remainders:
                    self._add_handlers(key[0], (key[1],) + remainder, h)
        for h in self._reverse.iterkeys():
            h(None)

# vim:sw=4:et:ai
