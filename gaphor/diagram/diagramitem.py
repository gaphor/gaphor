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
        'subject':        (gobject.TYPE_PYOBJECT, 'subject',
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
        self.__handler_to_id = { }
        # Add the class' on_subject_notify() as handler:
        self.connect('notify::subject', type(self).on_subject_notify)
        self.__subject_notifier_ids = (None,)
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
        """Connect a handler to signal name with args.
        Note that in order to connect to the subject property, you have
        to use "notify::subject".
        A signal handler id is returned.
        """
        id = CanvasItem.connect(self, name, handler, *args)
        key = (handler,) + args
        try:
            self.__handler_to_id[key].append(id)
        except:
            # it's a new entry:
            self.__handler_to_id[key] = [id]
        return id

    def disconnect(self, handler_or_id, *args):
        """Disconnect a signal handler. If handler_or_id is an integer (int)
        it is expected to be the signal handler id. Otherwise
        handler_or_id + *args are the same arguments passed to the connect()
        method (except the signal name). The latter form is used by
        gaphor.UML.Element.
        """
        if isinstance(handler_or_id, int):
            CanvasItem.disconnect(self, handler_or_id)
            for v in self.__handler_to_id.values():
                if handler_or_id in v:
                    v.remove(handler_or_id)
                    break
        else:
            try:
                ids = self.__handler_to_id[(handler_or_id,) + args]
            except KeyError, e:
                print e
            else:
                for id in ids:
                    CanvasItem.disconnect(self, id)
                del self.__handler_to_id[(handler_or_id,) + args]

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

    def on_subject_notify(self, pspec, notifiers=()):
        """A new subject is set on this model element.
        notifiers is an optional tuple of elements that also need a
        callback function. Callbacks have the signature
        on_subject_notify__<notifier>(self, subject, pspec).
        """
        log.info('DiagramItem.on_subject_notify: %s' % str(notifiers))
        old_subject = self.__subject_notifier_ids[0]
        for id in self.__subject_notifier_ids[1:]:
            old_subject.disconnect(id)
        self.__subject_notifier_ids = (None,)

        if self.subject:
            self.__subject_notifier_ids = [self.subject]
            for signal in notifiers:
                log.debug('DiaCanvasItem.on_subject_notify: %s' % signal)
                self.__subject_notifier_ids.append(self.subject.connect(signal,
                             getattr(self, 'on_subject_notify__%s' % signal)))

        self.request_update()

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

