# vim:sw=4:et

from gaphor.UML import Element, Presentation
from diacanvas import CanvasItem
import gobject
import gaphor.UML.properties.umlproperty

class diagramassociation(gaphor.UML.properties.umlproperty):
    """Specialized association for use in diagram items.
    It has the same interface as the association property defined in
    gaphor/UML/properties.py, but delegates everything to the GObject property
    handlers.
    """

    def notify(self, obj):
        # notification is done by set_property()
        pass

    def load(self, value):
        pass

    def save(self, save_func):
        pass

    def unlink(self, obj):
        obj.set_property(self.name, None)

    def _get(self, obj):
        return obj.get_property(self.name)

    def _set2(self, obj, value):
        obj.set_property(self.name, value)

    def _del(self, obj, value):
        obj.set_property(self.name, None)


class DiagramItem(Presentation):
    """Basic functionality for all model elements (lines and elements!).

    This class contains common functionallity for model elements and
    relationships.
    It provides an interface similar to UML.Element for connecting and
    disconnecting signals.

    This class is not very useful on its own. It functions as a base class
    for more concrete subclasses:
        class ModelElement(diacanvas.CanvasElement, DiagramItem):
            ...
    """

    # Prototype for signals emited by UML.Element
    signal_prototype = (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))

    # Override the original subject as defined in UML.Presentation:
    subject = diagramassociation('subject', Element, upper=1, opposite='presentation')

    def __init__(self, id=None):
        Presentation.__init__(self, id)
        self.saved_subject = None
        self.handler_to_id = { }
        self.connect('notify::parent', DiagramItem.on_parent_notify)
        self.connect('__unlink__', self.on_unlink)

    # UML.Element interface used by properties:

    def unlink(self):
        """Send the unlink signal and remove itself from the canvas
        """
        self.emit('__unlink__', '__unlink__')

    def on_unlink(self, signal_name):
        if self.parent:
                self.parent.remove(self)

    def connect(self, name, handler, *args):
        """Let UML.Element specific signals be handled by the Element and
        other signals by CanvasItem.
        """
        id = CanvasItem.connect(self, name, handler, *args)
        key = (handler,) + args
        ids = self.handler_to_id.get(key)
        if not ids:
            self.handler_to_id[key] = (id,)
        else:
            self.handler_to_id[key] = ids + (id,)
        return id

    def disconnect(self, handler_or_id, *args):
        """Call GObject.disconnect() or UML.Element.disconnect() depending
        on if handler_or_id is an id or a method.
        """
        if type(handler_or_id) == type(1):
            try:
                ids = self.handler_to_id[(handler_or_id,) + args]
            except KeyError, e:
                print e
            else:
                for id in ids:
                    CanvasItem.disconnect(self, id)
        else:
            CanvasItem.disconnect(self, handler_or_id)

    def notify(self, name):
        """Emit a signal with as first argument the signal's name.
        """
        self.emit(name, name)

    def get_subject(self, x=None, y=None):
        """Get the subject that is represented by this diagram item.
        A (x,y) coordinate can be given (relative to the item) so a
        diagram item can return another subject that the default when the
        mouse pointer is on a specific place over the item.
        """
        return self.subject

    def has_capability(self, capability):
        """Returns the availability of an diagram item specific capability.
        This kinda works the same way as capabilities on windows.
        """
        return False

    def save_property(self, save_func, name):
        """Save a property, this is a shorthand method.
        """
        save_func(name, self.get_property(name))

    def on_parent_notify (self, parent):
        if self.parent and self.subject:
            self.saved_subject = self.subject
            del self.subject[self]
        elif not self.parent and self.saved_subject:
            self.subject = self.saved_subject
            self.saved_subject = None

#    def on_subject_changed(self, name):
#        pass

    # DiaCanvasItem callbacks
    def _on_glue(self, handle, wx, wy, parent_class):
        if handle.owner.allow_connect_handle (handle, self):
            #print self.__class__.__name__, 'Glueing allowed.'
            return parent_class.on_glue (self, handle, wx, wy)
        #else:
            #print self.__class__.__name__, 'Glueing NOT allowed.'
        # Dummy value with large distance value
        return None

    def _on_connect_handle (self, handle, parent_class):
        if handle.owner.allow_connect_handle (handle, self):
            #print self.__class__.__name__, 'Connection allowed.'
            ret = parent_class.on_connect_handle (self, handle)
            if ret != 0:
                handle.owner.confirm_connect_handle(handle)
                return ret
        #else:
            #print self.__class__.__name__, 'Connection NOT allowed.'
        return 0

    def _on_disconnect_handle (self, handle, parent_class):
        if handle.owner.allow_disconnect_handle (handle):
            #print self.__class__.__name__, 'Disconnecting allowed.'
            ret = parent_class.on_disconnect_handle (self, handle)
            if ret != 0:
                handle.owner.confirm_disconnect_handle(handle, self)
                return ret
        #else:
            #print self.__class__.__name__, 'Disconnecting NOT allowed.'
        return 0

