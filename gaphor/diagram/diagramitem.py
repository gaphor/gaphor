# vim:sw=4:et
"""DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

import gobject
from diacanvas import CanvasItem

from gaphor import resource
import gaphor.misc.uniqueid as uniqueid
from gaphor.UML import Element, Presentation
from gaphor.UML.properties import association


class diagramassociation(association):
    """Specialized association for use in diagram items.
    It has the same interface as the association property defined in
    gaphor/UML/properties.py, but delegates everything to the GObject property
    handlers.
    """

    # TODO: Maybe we should not break our side of the association...
    #       Since signals are still connected as the diagram item is unlinked.

    def unlink(self, obj):
        #print 'diagramassociation.unlink', obj, value
        obj.preserve_property(self.name)
        association.unlink(self, obj)

    def _set2(self, obj, value):
        #print 'diagramassociation._set2', obj, value
        obj.preserve_property(self.name)
        if obj.canvas and obj.canvas.in_undo and len(value.presentation) == 0:
            print 'diagramassociation._set2(): relinking!'
            value.relink()
        return association._set2(self, obj, value)

    def _del(self, obj, value):
        #print 'diagramassociation._del', obj, value, value.id
        obj.preserve_property(self.name)
        # TODO: Add some extra notification here to tell the diagram
        # item that the reference is about to be removed.
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

    This class is not very useful on its own. It contains some glue-code for
    diacanvas.DiaCanvasItem and gaphor.UML.Element.

    Example:
        class ElementItem(diacanvas.CanvasElement, DiagramItem):
            connect = DiagramItem.connect
            disconnect = DiagramItem.disconnect
            ...
    """
    __gproperties__ = {
        'subject':        (gobject.TYPE_PYOBJECT, 'subject',
                         'subject held by the diagram item',
                         gobject.PARAM_READWRITE),
    }

    __gsignals__ = {
        '__unlink__': (gobject.SIGNAL_RUN_FIRST,
                       gobject.TYPE_NONE, (gobject.TYPE_STRING,))
    }

    # Override the original subject as defined in UML.Presentation:
    # Note that subject calls GObject.notify to emit changes
    subject = diagramassociation('subject', Element, upper=1, opposite='presentation')

    popup_menu = ()

    def __init__(self, id=None):
        Presentation.__init__(self)
        self._id = id # or uniqueid.generate_id()

        # Mapping to convert handlers to GObject signal ids.
        self.__handler_to_id = { }

        # Add the class' on_subject_notify() as handler:
        self.connect('notify::subject', type(self).on_subject_notify)

        # __the_subject is a backup that is used to disconnect signals when a
        # new subject is set (or the original one is removed)
        self.__the_subject = None

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
            #print 'loading subject', value
            type(self).subject.load(self, value)
        else:
            #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
            try:
                self.set_property(name, eval(value))
            except:
                log.warning('%s has no property named %s (value %s)' % (self, name, value))

    def postload(self):
        if self.subject:
            self.on_subject_notify(type(self).subject)

    def unlink(self):
        """Send the unlink signal and remove itself from the canvas.
        """
        #log.debug('DiagramItem.unlink(%s)' % self)
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

    # gaphor.UML.Element like signal interface:

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
            for v in self.__handler_to_id.itervalues():
                if handler_or_id in v:
                    v.remove(handler_or_id)
                    break
        else:
            try:
                key = (handler_or_id,) + args
                ids = self.__handler_to_id[key]
            except KeyError, e:
                log.error("Couldn't retrieve connection handle ids", e)
            else:
                for id in ids:
                    CanvasItem.disconnect(self, id)
                del self.__handler_to_id[key]

    def notify(self, name, pspec=None):
        CanvasItem.notify(self, name)

    def save_property(self, save_func, name):
        """Save a property, this is a shorthand method.
        """
        save_func(name, self.get_property(name))

    def save_properties(self, save_func, *names):
        """Save a property, this is a shorthand method.
        """
        for name in names:
            self.save_property(save_func, name)

    def get_popup_menu(self):
        return self.popup_menu

    def _subject_connect_helper(self, element, callback_prefix, prop_list):
        """Connect a signal notifier. The notifier can be just the name of
        one of the subjects properties.

        See: DiagramItem.on_subject_notify()
        """
        prop = prop_list[0]
        callback_name = '%s_%s' % (callback_prefix, prop)
        if len(prop_list) == 1:
            #log.debug('_subject_connect_helper - %s' % callback_name)
            handler = getattr(self, callback_name)
            element.connect(prop, handler)
            # Call the handler, so it can update its state
            #handler(prop, getattr(type(element), prop))
            #handler(element, getattr(type(element), prop))
        else:
            p = getattr(element, prop)
            #log.debug('_subject_connect_helper 2 - %s' % prop)
            pl = prop_list[1:]
            element.connect(prop, self._on_subject_notify_helper, callback_name, pl, p)
            if p:
                self._subject_connect_helper(p, callback_name, pl)
            else:
                pass

    def _subject_disconnect_helper(self, element, callback_prefix, prop_list):
        """Disconnect a previously connected signal handler.

        See: DiagramItem.on_subject_notify()
        """
        prop = prop_list[0]
        callback_name = '%s_%s' % (callback_prefix, prop)
        if len(prop_list) == 1:
            #log.debug('_subject_disconnect_helper - %s' % callback_name)
            handler = getattr(self, callback_name)
            element.disconnect(handler)
            # Call the handler, so it can update its state
            #handler(element, getattr(type(element), prop))
        else:
            p = getattr(element, prop)
            #log.debug('_subject_disconnect_helper 2 - %s' % prop)
            pl = prop_list[1:]
            element.disconnect(self._on_subject_notify_helper, callback_name, pl, p)
            if p:
                self._subject_disconnect_helper(p, callback_name, pl)
            else:
                # TODO: Maybe do an update here to, if p is None.
                pass

    def _on_subject_notify_helper(self, element, pspec, callback_name, prop_list, old):
        """This signal handler handles signals that are not direct properties
        of self.subject (e.g. 'subject.lowerValue.value'). This way the presentation class is
        not bothered with the details of keeping track of those properties.

        NOTE: This only works for properties with multiplicity [0..1] or [1].

        See: DiagramItem.on_subject_notify()
        """
        name = pspec.name
        prop = getattr(element, name)
        if prop is not old:
            # Attach a new signal handler with the new 'old' value:
            if old:
                self._subject_disconnect_helper(old, callback_name, prop_list)
            if prop:
                self._subject_connect_helper(prop, callback_name, prop_list)

    def on_subject_notify(self, pspec, notifiers=()):
        """A new subject is set on this model element.
        notifiers is an optional tuple of elements that also need a
        callback function. Callbacks have the signature
        on_subject_notify__<notifier>(self, subject, pspec).

        A notifier can be a property of subject (e.g. 'name') or a property
        of a property of subject (e.g. 'lowerValue.value').
        """
        #log.info('DiagramItem.on_subject_notify: %s' % self.__subject_notifier_ids)
        # First, split all notifiers on '.'
        callback_prefix = 'on_subject_notify_'
        notifiers = map(str.split, notifiers, ['.'] * len(notifiers))
        old_subject = self.__the_subject
        subject_connect_helper = self._subject_connect_helper
        subject_disconnect_helper = self._subject_disconnect_helper

        if old_subject:
            for n in notifiers:
                #self._subject_disconnect(self.__the_subject, n)
                subject_disconnect_helper(old_subject, callback_prefix, n)

        if self.subject:
            subject = self.__the_subject = self.subject
            for n in notifiers:
                #log.debug('DiaCanvasItem.on_subject_notify: %s' % signal)
                #self._subject_connect(self.subject, n)
                subject_connect_helper(subject, callback_prefix, n)
        # Execute some sort of ItemNewSubject action
        try:
            main_window = resource('MainWindow')
        except KeyError:
            pass
        else:
            main_window.execute_action('ItemNewSubject')
        self.request_update()

    # DiaCanvasItem callbacks

    def _on_glue(self, handle, wx, wy, parent_class):
        """This function is used to notify the connecting item
        about being connected. handle.owner.allow_connect_handle() is
        called to determine if a connection is allowed.
        """
        if handle.owner.allow_connect_handle (handle, self):
            #print self.__class__.__name__, 'Glueing allowed.'
            return parent_class.on_glue (self, handle, wx, wy)
        #else:
            #print self.__class__.__name__, 'Glueing NOT allowed.'
        # Dummy value with large distance value
        return None

    def _on_connect_handle (self, handle, parent_class):
        """This function is used to notify the connecting item
        about being connected. handle.owner.allow_connect_handle() is
        called to determine if a connection is allowed. If the connection
        succeeded handle.owner.confirm_connect_handle() is called.
        """
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
        """Use this function to disconnect handles. It notifies
        the connected item about being disconnected.
        handle.owner.allow_disconnect_handle() is
        called to determine if a connection is allowed to be removed.
        If the disconnect succeeded handle.owner.confirm_connect_handle()
        is called.
        """
        if handle.owner.allow_disconnect_handle (handle):
            #print self.__class__.__name__, 'Disconnecting allowed.'
            ret = parent_class.on_disconnect_handle (self, handle)
            if ret != 0:
                handle.owner.confirm_disconnect_handle(handle, self)
                # TODO: call ConnectAction
                return ret
        #else:
            #print self.__class__.__name__, 'Disconnecting NOT allowed.'
        return 0

