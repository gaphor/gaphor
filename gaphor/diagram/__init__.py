"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import inspect
import gobject

from gaphor.misc import uniqueid
from gaphor.diagram.style import Style

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, uniqueid.generate_id())

def create_as(type, id):
    return type(id)

def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)

def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item


def namedelement(f):
    """
    Decorator for named items constructors. Injects name text element into
    an object.
    """
    def wrapper(*args, **kw):
        obj = args[0]
        f(*args, **kw)

        style = {
                'text-align': obj.style.name_align,
                'text-padding': obj.style.name_padding,
                'text-outside': obj.style.name_outside,
                'text-align-group': 'stereotype',
        }
        obj._name = obj.add_text('name', style=style, editable=True)

    return wrapper


def nd_subject(f):
    """
    Named item subject notification decorator. Updates subject notification
    with subject's name notification.
    """
    def wrapper(obj, pspec, notifiers=()):
        notifiers = ('name',) + notifiers
        f(obj, pspec, notifiers)
        if obj.subject:
            obj.on_subject_notify__name(obj.subject)
        obj.request_update()
    return wrapper


def nd_subject_name(f):
    """
    Named item subject name notification decorator. Updates text of name text
    element.
    """
    def wrapper(obj, subject, pspec=None):
        obj._name.text = subject.name
        f(obj, subject, pspec)
        
    return wrapper


class DiagramItemMeta(type):
    """
    Initialize a new diagram item.
    1. Register UML.Elements by means of the __uml__ attribute (see
       map_uml_class method).
    2. Set items style information.

    @ivar style: style information
    """

    def __init__(self, name, bases, data):
        type.__init__(self, name, bases, data)

        self.map_uml_class(data)
        self.set_style(data)
        self.set_namedelement(data)


    def set_namedelement(self, data):
        """
        If an diagram item is named element, then inject appropriate
        decorators and notification methods.
        """
        if '__namedelement__' in data and data['__namedelement__']:

            cls = self
            def subject_notification(self, pspec, notifiers=()):
                super(cls, self).on_subject_notify(pspec, ('name',) + notifiers)
                if self.subject:
                    self.on_subject_notify__name(self.subject)
                self.request_update()


            def name_notification(self, subject, pspec=None):
                self._name.text = subject.name
                self.request_update()


            # inject or decorate notification methods
            if hasattr(self, 'on_subject_notify'):
                self.on_subject_notify = nd_subject(self.on_subject_notify)
            else:
                self.on_subject_notify = subject_notification

            if hasattr(self, 'on_subject_notify__name'):
                self.on_subject_notify__name = nd_subject_name(self.on_subject_notify__name)
            else:
                self.on_subject_notify__name = name_notification

            # decorate constructor
            self.__init__ = namedelement(self.__init__)


    def map_uml_class(self, data):
        """
        Map UML class to diagram item.

        @param cls:  new instance of item class
        @param data: metaclass data with UML class information 

        """
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, self)
            else:
                set_diagram_item(obj, self)


    def set_style(self, data):
        """
        Set item style information by merging provided information with
        style information from base classes.

        @param cls:   new instance of diagram item class
        @param bases: base classes of an item
        @param data:  metaclass data with style information
        """
        style = Style()
        for c in self.__bases__:
            if hasattr(c, 'style'):
                for (name, value) in c.style.items():
                    style.add(name, value)

        if '__style__' in data:
            for (name, value) in data['__style__'].iteritems():
                style.add(name, value)

        self.style = style


# vim:sw=4:et
