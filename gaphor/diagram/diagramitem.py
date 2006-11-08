# vim:sw=4:et
"""DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

from gaphor import resource
from gaphor import UML
from gaphor.misc import uniqueid
from gaphor.UML import Element, Presentation
from gaphor.diagram import DiagramItemMeta

STEREOTYPE_OPEN  = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class DiagramItem(Presentation, Element):
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

    @cvar style: styles information (derived from DiagramItemMeta)
    """

    __metaclass__ = DiagramItemMeta

    stereotype_list = []
    popup_menu = ('Stereotype', stereotype_list)

    def __init__(self, id=None):
        Element.__init__(self)
        Presentation.__init__(self)
        self._id = id # or uniqueid.generate_id()

        # Add the class' on_subject_notify() as handler:
        self.connect('subject', type(self).on_subject_notify)

        # __the_subject is a backup that is used to disconnect signals when a
        # new subject is set (or the original one is removed)
        self.__the_subject = None

        # properties, which should be saved in file
        self._persistent_props = set()

        # stereotype
        self._stereotype = None

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
            save_func(p, getattr(self, p.replace('-', '_')))


    def load(self, name, value):
        if name == 'subject':
            print self, 'loading subject', value
            type(self).subject.load(self, value)
            print self, 'subject =', self.subject
        else:
            #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
            try:
                setattr(self, name, eval(value))
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

#    def set_subject(self, subject=None):
#        """Set the subject. In addition, if there are no more presentations
#        on the subject, the subject is unlink()'ed.
#        Note that this function is different from setting the subject property
#        directly!
#        """
#        #log.debug('set_subject %s %s' % (self.subject, subject))
#        old = self.subject
#
#        # remove the subject if we have one
#        if self.subject:
#            del self.subject
#
#        if old and len(old.presentation) == 0:
#            #log.debug('diagramitem.unlink: No more presentations: unlinking')
#            old.unlink()
#         
#        self.subject = subject

    def get_popup_menu(self):
        """In the popup menu a submenu is created with Stereotypes than can be
        applied to this classifier (Class, Interface).
        If the class itself is a metaclass, an option is added to check if the class
        exists.
        """
        subject = self.subject
        stereotype_list = self.stereotype_list
        stereotype_list[:] = []

        # UML specs does not allow to extend stereotypes with stereotypes
        if subject and not isinstance(subject, UML.Stereotype):
            # look for stereotypes to put them into context menu of an item
            # this can be only done when subject exists

            from gaphor.actions.itemactions import ApplyStereotypeAction, register_action

            cls = type(subject)

            # find out names of classes, which are superclasses of our
            # subject
            names = set(c.__name__ for c in cls.__mro__ if issubclass(c, Element))

            # find stereotypes that extend out metaclass
            classes = subject._factory.select(lambda e: e.isKindOf(UML.Class) and e.name in names)

            for class_ in classes:
                for extension in class_.extension:
                    stereotype = extension.ownedEnd.type
                    stereotype_action = ApplyStereotypeAction(stereotype)
                    register_action(stereotype_action, 'ItemFocus')
                    stereotype_list.append(stereotype_action.id)
        return self.popup_menu

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
        """Disconnect a previously connected signal handler.

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
        """This signal handler handles signals that are not direct properties
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
        notifiers = map(str.split, notifiers + ('appliedStereotype',), ['.'] * len(notifiers))
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
                self.update_stereotype()

        # Execute some sort of ItemNewSubject action
        try:
            main_window = resource('MainWindow')
        except KeyError:
            pass
        else:
            main_window.execute_action('ItemNewSubject')
        self.request_update()


    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
        if self.subject:
            self.update_stereotype()

    def request_update(self):
        pass

    #
    # Stereotypes
    #
    def get_stereotype(self):
        if self._stereotype:
            return self._stereotype

    def set_stereotype(self, text=None):
        """
        Set the stereotype text for the diagram item.

        Note, that text is not Stereotype object.

        @arg text: stereotype text
        """
        if text:
            self._stereotype = STEREOTYPE_OPEN + text + STEREOTYPE_CLOSE
        else:
            self._stereotype = None
        self.request_update()

    stereotype = property(get_stereotype, set_stereotype)

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

    #
    # utility methods
    #

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
                ok = isinstance(subject, cls)
            if predicate:
                ok = predicate(self)

            if ok:
                return stereotype
        return None
