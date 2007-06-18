# vim:sw=4:et
"""DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

from gaphor import UML
from gaphor.misc import uniqueid
from gaphor.UML import Element, Presentation
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.textelement import EditableTextSupport
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_TOP

STEREOTYPE_OPEN  = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class SubjectSupport(Presentation, Element):
    """
    Support class that adds support methods for Presentation.subject.

    This is a support class that should could be added to subclasses of
    UML.Presentation.
    """

    def __init__(self):
        Presentation.__init__(self)
        Element.__init__(self)
        # Add the class' on_subject_notify() as handler:
        self.connect('subject', type(self).on_subject_notify)

        # __the_subject is a backup that is used to disconnect signals when a
        # new subject is set (or the original one is removed)
        self.__the_subject = None

    def _subject_connect_helper(self, element, callback_prefix, prop_list):
        """Connect a signal notifier. The notifier can be just the name of
        one of the subjects properties.

        See: DiagramItem.on_subject_notify()
        """
        #log.debug('_subject_connect_helper: %s %s %s' % (element, callback_prefix, prop_list))

        prop = prop_list[0]
        callback_name = '%s_%s' % (callback_prefix, prop)
        if len(prop_list) == 1:
            #log.debug('_subject_connect_helper - %s %s' % (element, callback_name))
            handler = getattr(self, callback_name)
            element.connect(prop, handler)
            # Call the handler, so it can update its state
            #handler(prop, getattr(type(element), prop))
            #handler(element, getattr(type(element), prop))
        else:
            p = getattr(element, prop)
            #log.debug('_subject_connect_helper 2 - %s: %s' % (prop, p))
            pl = prop_list[1:]
            element.connect(prop, self._on_subject_notify_helper, callback_name, pl, [p])
            if p:
                self._subject_connect_helper(p, callback_name, pl)
            else:
                pass

    def _subject_disconnect_helper(self, element, callback_prefix, prop_list):
        """
        Disconnect a previously connected signal handler.

        See: DiagramItem.on_subject_notify()
        """
        #log.debug('_subject_disconnect_helper: %s %s %s' % (element, callback_prefix, prop_list))
        prop = prop_list[0]
        callback_name = '%s_%s' % (callback_prefix, prop)
        if len(prop_list) == 1:
            #log.debug('_subject_disconnect_helper - %s %s' % (element, callback_name))
            handler = getattr(self, callback_name)
            element.disconnect(handler)
            # Call the handler, so it can update its state
            #handler(element, getattr(type(element), prop))
        else:
            p = getattr(element, prop)
            #log.debug('_subject_disconnect_helper 2 - %s' % prop)
            pl = prop_list[1:]
            element.disconnect(self._on_subject_notify_helper, callback_name, pl, [p])
            if p:
                self._subject_disconnect_helper(p, callback_name, pl)
            else:
                pass

    def _on_subject_notify_helper(self, element, pspec, callback_name, prop_list, old):
        """
        This signal handler handles signals that are not direct properties
        of self.subject (e.g. 'subject.lowerValue.value'). This way the
        presentation class is not bothered with the details of keeping track
        of those properties.

        NOTE: This only works for properties with multiplicity [0..1] or [1].

        See: DiagramItem.on_subject_notify()
        """
        name = pspec.name
        prop = getattr(element, name)
        #log.debug('_on_subject_notify_helper: %s %s %s %s %s' % (element, name, callback_name, prop_list, old))
        # Attach a new signal handler with the new 'old' value:
        if old[0]:
            #log.info('disconnecting')
            self._subject_disconnect_helper(old[0], callback_name, prop_list)
        if prop:
            self._subject_connect_helper(prop, callback_name, prop_list)

        # Set the new "old" value
        old[0] = prop

    def on_subject_notify(self, pspec, notifiers=()):
        """
        A new subject is set on this model element.
        notifiers is an optional tuple of elements that also need a
        callback function. Callbacks have the signature
        on_subject_notify__<notifier>(self, subject, pspec).

        A notifier can be a property of subject (e.g. 'name') or a property
        of a property of subject (e.g. 'lowerValue.value').
        """
        #log.info('Setting subject from %s to %s' % (self.__the_subject, self.subject))
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

        self.request_update()


class StereotypeSupport(object):
    """
    Support methods for stereotypes.
    """
    STEREOTYPE_ALIGN = {
        'text-align'  : (ALIGN_CENTER, ALIGN_TOP),
        'text-padding': (5, 10, 2, 10),
        'text-outside': False,
        'text-align-group': 'stereotype',
    }

    def __init__(self):
        self._stereotype = self.add_text('stereotype',
                style=self.STEREOTYPE_ALIGN,
                pattern='%s%%s%s' % (STEREOTYPE_OPEN, STEREOTYPE_CLOSE),
                when=self.display_stereotype)


    def display_stereotype(self):
        """
        Display stereotype if it is not empty.
        """
        return self._stereotype.text


    def set_stereotype(self, text=None):
        """
        Set the stereotype text for the diagram item.

        Note, that text is not Stereotype object.

        @arg text: stereotype text
        """
        self._stereotype.text = text
        self.request_update()

    stereotype = property(lambda s: s._stereotype, set_stereotype)

    def update_stereotype(self):
        """
        Update the stereotype definitions (text) of this item.

        Note, that this method is also called from
        ExtensionItem.confirm_connect_handle method.
        """
        if self.subject:
            applied_stereotype = self.subject.appliedStereotype
        else:
            applied_stereotype = None

        def stereotype_name(name):
            """
            Return a nice name to display as stereotype. First will be
            character lowercase unless the second character is uppercase.
            """
            if len(name) > 1 and name[1].isupper():
                return name
            else:
                return name[0].lower() + name[1:]

        # by default no stereotype, however check for __stereotype__
        # attribute to assign some static stereotype see interfaces,
        # use case relationships, package or class for examples
        stereotype = getattr(self, '__stereotype__', None)
        if stereotype:
            stereotype = self.parse_stereotype(stereotype)

        if applied_stereotype:
            # generate string with stereotype names separated by coma
            sl = ', '.join(stereotype_name(s.name) for s in applied_stereotype)
            if stereotype:
                stereotype = '%s, %s' % (stereotype, sl)
            else:
                stereotype = sl

        # Phew! :]
        self.set_stereotype(stereotype)

    def parse_stereotype(self, data):
        if isinstance(data, str): # return data as stereotype if it is a string
            return data

        subject = self.subject

        for stereotype, condition in data.items():
            if isinstance(condition, tuple):
                cls, predicate = condition
            elif isinstance(condition, type):
                cls = condition
                predicate = None
            elif callable(condition):
                cls = None
                predicate = condition
            else:
                assert False, 'wrong conditional %s' % condition

            ok = True
            if cls:
                ok = type(subject) is cls #isinstance(subject, cls)
            if predicate:
                ok = predicate(self)

            if ok:
                return stereotype
        return None


class DiagramItem(SubjectSupport, StereotypeSupport, EditableTextSupport):
    """
    Basic functionality for all model elements (lines and elements!).

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

    @cvar style: styles information (derived from DiagramItemMeta)
    """

    __metaclass__ = DiagramItemMeta

    def __init__(self, id=None):
        SubjectSupport.__init__(self)
        EditableTextSupport.__init__(self)
        StereotypeSupport.__init__(self)

        self._id = id

        # properties, which should be saved in file
        self._persistent_props = set()

    id = property(lambda self: self._id, doc='Id')

    def set_prop_persistent(self, name):
        """Specify property of diagram item, which should be saved in file.
        """
        self._persistent_props.add(name)


    # UML.Element interface used by properties:

    # TODO: Use adapters for load/save functionality
    def save(self, save_func):
        if self.subject:
            save_func('subject', self.subject)

        # save persistent properties
        for p in self._persistent_props:
            save_func(p, getattr(self, p.replace('-', '_')), reference=True)


    def load(self, name, value):
        if name == 'subject':
            type(self).subject.load(self, value)
        else:
            #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
            try:
                setattr(self, name.replace('-', '_'), eval(value))
            except:
                log.warning('%s has no property named %s (value %s)' % (self, name, value))

    def postload(self):
        if self.subject:
            self.on_subject_notify(type(self).subject)

    def save_property(self, save_func, name):
        """Save a property, this is a shorthand method.
        """
        save_func(name, getattr(self, name.replace('-', '_')))

    def save_properties(self, save_func, *names):
        """Save a property, this is a shorthand method.
        """
        for name in names:
            self.save_property(save_func, name)

    def unlink(self):
        """
        Remove the item from the canvas and set subject to None.
        """
        if self.canvas:
            self.canvas.remove(self)
        self.subject = None
        super(DiagramItem, self).unlink()

    def item_at(self, x, y):
        return self

    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
        if self.subject:
            self.request_update()

    def request_update(self):
        """Placeholder for gaphor.Item's request_update() method.
        """
        pass

    def on_subject_notify(self, pspec, notifiers=()):
        SubjectSupport.on_subject_notify(self, pspec, notifiers + ('appliedStereotype',))



# vim:sw=4:et:ai
