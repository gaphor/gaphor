"""
"""

from zope import interface, component
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.UML.interfaces import IElementChangeEvent


class ElementBasedDispatcher(object):
    """
    The Element based Dispatcher allows handlers to receive only events
    concerining certain elements. 

    The element of interest can be defined as a "path".

    The handlers are registered on their property attribute. This avoids
    subclass lookups and is pretty specific. 

    On an event two things happen:
    1. An event handler is called (if any)::

        (event.property, event.element) -> set(handlers)

    2. Handlers interested in the other end of the association are added as handlers (or removed)
    E.g. Transition.guard.value is defined as path 'subject.guard.value'
    If a subject is assigned a guard object it should also invoke the handler
    If guard has a value it should also trigger the invocation. Of course only
    one invocation of the handler is required.

    Need to register which other elements are involved in a path.

      Class.operation.parameter[n].name

    Also note that the direction is usually one-directional (-->)!.

    Do handlers for (Operation, someelement) are added through Class.operation.

    On deletion of Class.operation, we should also check for Operation.parameter and parameter.name references in the handlers table.

    ==> Need a table handler -> (path tuple)
    Given the path (tuple of assocations (+ attribute))
    """

    interface.implements(IService)

    def __init__(self):
        # Handlers is a dict of sets
        # (event.element, event.property): set([(handler, path), ..])
        self._handlers = dict()

    def init(self, app):
        self._app = app
        app.register_handler(self.on_element_change_event)

    def shutdown(self):
        self._app.unregister_handler(self.on_element_change_event)
        self._app = None

    def _path_to_properties(self, element, path):
        """
        Given a start element and a path, return a tuple of UML properties
        (association, attribute, etc.) representing the path.

        >>> from gaphor import UML
        >>> dispatcher = ElementBasedDispatcher()
        >>> map(str, dispatcher._path_to_properties(UML.Class(), 'ownedOperation.parameter.name')) # doctest: +NORMALIZE_WHITESPACE
        ['<association ownedOperation: Operation[0..*] <>-> class_>',
        "<derivedunion parameter:
            '<association returnResult: Parameter[0..*] <>-> ownerReturnParam>',
            '<association formalParameter: Parameter[0..*] <>-> ownerFormalParam>'>",
        "<attribute name: <type 'str'>[0..1] = None>"]
        """
        c = type(element)
        tpath = []
        for attr in path.split('.'):
            prop = getattr(c, attr)
            tpath.append(prop)
            c = prop.type
        return tuple(tpath)


    def _add_handlers(self, element, props, handler):
        """
        Provided an element and a path of properties (props), register the
        handler for each property.

        """
        property, remainder = props[0], props[1:]
        try:
            handlers = self._handlers[element, property]
        except KeyError:
            handlers = set()
            self._handlers[element, property] = handlers
        handlers.add((handler, remainder))
        if remainder:
            if property.upper > 1:
                for e in property._get(element):
                    self._add_handlers(e, remainder, handler)
            else:
                e = property._get(element)
                if e:
                    self._add_handlers(e, remainder, handler)


    def _remove_handlers(self, element, property, handler):
        """
        Remove the handler of the path of elements.

        """
        handlers = self._handlers.get((element, property))
        if not handlers:
            return

        for h, remainder in list(handlers):
            if h is handler:
                if remainder:
                    if property.upper > 1:
                        for e in property._get(element):
                            self._remove_handlers(e, remainder[0], handler)
                    else:
                        e = property._get(element)
                        if e:
                            self._remove_handlers(e, remainder[0], handler)
            handlers.remove((h, remainder))
        if not handlers:
            del self._handlers[element, property]


    def register_handler(self, element, path, handler):
        props = self._path_to_properties(element, path)
        self._add_handlers(element, props, handler)

    # We want: def unregister_handler(self, handler):
    def unregister_handler(self, element, property, handler):
        self._remove_handlers(element, property, handler)

    def unregister_all_handlers(self, element):
        # May be useful when listening to elementDelete events
        pass

    @component.adapter(IElementChangeEvent)
    def on_element_change_event(self, event):
        handlers = self._handlers.get((event.property, event.element))
        if handlers:
            for handler, _ in handlers:
                try:
                    handler(event)
                except Exception, e:
                    log.error('problem executing handler %s' % handler, e)
        # TODO: handle add/removal of items in self._handlers

# vim:sw=4:et:ai
