# vim:sw=4:et
"""DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

from gaphor.UML import Element, Presentation
from diacanvas import CanvasItem
import gobject
from gaphor.UML.properties import association


class diagramassociation(association):
    """Specialized association for use in diagram items.
    It has the same interface as the association property defined in
    gaphor/UML/properties.py, but delegates everything to the GObject property
    handlers.
    """

    def unlink(self, obj):
        #print 'diagramassociation.unlink', obj, value
        obj.preserve_property('subject')
        association.unlink(self, obj)

    def _set2(self, obj, value):
        #print 'diagramassociation._set2', obj, value
        obj.preserve_property('subject')
        if obj.canvas and obj.canvas.in_undo and len(value.presentation) == 0:
            print 'diagramassociation._set2(): relinking!'
            value.relink()
        return association._set2(self, obj, value)

    def _del(self, obj, value):
        #print 'diagramassociation._del', obj, value, obj._subject
        obj.preserve_property('subject')
        association._del(self, obj, value)
        if len(value.presentation) == 0 or \
           len(value.presentation) == 1 and obj in value.presentation:
            #log.debug('diagramassociation._del: No more presentations: unlinking')
            value.unlink()
        

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
    __gproperties__ = {
	'subject':	(gobject.TYPE_PYOBJECT, 'subject',
			 'subject held by the model element',
			 gobject.PARAM_READWRITE),
    }

    __gsignals__ = {
	'__unlink__': (gobject.SIGNAL_RUN_FIRST,
                       gobject.TYPE_NONE, (gobject.TYPE_STRING,))
    }

    # Override the original subject as defined in UML.Presentation:
    # Note that subject calls GObject.notify to emit changes
    subject = diagramassociation('subject', Element, upper=1, opposite='presentation')

    def __init__(self, id=None):
        Presentation.__init__(self)
        self._id = id
        self.handler_to_id = { }
        #self.connect('notify::parent', DiagramItem.on_parent_notify)
        #self.connect('__unlink__', self.on_unlink)

    id = property(lambda self: self._id, doc='Id')

    def do_set_property(self, pspec, value):
	if pspec.name == 'subject':
            #print 'set subject:', value
            if value:
                self.subject = value
            elif self.subject:
                del self.subject
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'subject':
	    return self.subject
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    # UML.Element interface used by properties:

    def save(self, save_func):
        if self.subject:
            save_func('subject', self.subject)

    def load(self, name, value):
        if name == 'subject':
            self.subject = value

    def postload(self):
        pass

    def unlink(self):
        """Send the unlink signal and remove itself from the canvas.
        """
        log.debug('DiagramItem.unlink(%s)' % self)
        # emit the __unlink__ signal the way UML.Element would have done:
        self.emit('__unlink__', '__unlink__')
        # remove the subject if we have one
        if self.subject:
            del self.subject
        self.set_property('parent', None)

    def relink(self):
        """Relinking is done by popping the undo stack...
        """
        log.info('RELINK DiagramItem')
        #self.emit('__unlink__', '__relink__')


    def connect(self, name, handler, *args):
        """Let UML.Element specific signals be handled by the Element and
        other signals by CanvasItem.
        Note that in order to connect to the subject property, you have
        to use "notify::subject".
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
        if isinstance(handler_or_id, int):
            CanvasItem.disconnect(self, handler_or_id)
        else:
            try:
                ids = self.handler_to_id[(handler_or_id,) + args]
            except KeyError, e:
                print e
            else:
                for id in ids:
                    CanvasItem.disconnect(self, id)
                del self.handler_to_id[(handler_or_id,) + args]

#    def notify(self, name):
#        """Emit a signal with as first argument the signal's name.
#        """
#        # Use GObject.notify() for the subject property
#        if name == 'subject':
#            DiaCanvasItem.notify(self, name)
#        else:
#            self.emit(name, name)

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

