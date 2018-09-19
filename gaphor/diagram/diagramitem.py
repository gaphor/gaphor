#!/usr/bin/env python

# Copyright (C) 2002-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         slmm <noreply@example.com>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

from __future__ import absolute_import
from zope import component
from gaphas.state import observed, reversible_property

from logging import getLogger
from gaphor.UML import uml2, modelfactory
from gaphor.services.elementdispatcher import EventWatcher
from gaphor.core import inject
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.textelement import EditableTextSupport
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_TOP
import six

logger = getLogger('Diagram')


class StereotypeSupport(object):
    """
    Support for stereotypes for every diagram item.
    """
    STEREOTYPE_ALIGN = {
        'text-align': (ALIGN_CENTER, ALIGN_TOP),
        'text-padding': (5, 10, 2, 10),
        'text-outside': False,
        'text-align-group': 'stereotype',
        'line-width': 2,
    }

    def __init__(self):
        self._stereotype = self.add_text('stereotype',
                                         style=self.STEREOTYPE_ALIGN,
                                         visible=lambda: self._stereotype.text)
        self._show_stereotypes_attrs = False

    @observed
    def _set_show_stereotypes_attrs(self, value):
        self._show_stereotypes_attrs = value
        self.update_stereotypes_attrs()

    show_stereotypes_attrs = reversible_property(
        fget=lambda s: s._show_stereotypes_attrs,
        fset=_set_show_stereotypes_attrs,
        doc="""
            Diagram item should show stereotypes attributes when property
            is set to True.

            When changed, method `update_stereotypes_attrs` is called.
            """)

    def update_stereotypes_attrs(self):
        """
        Update display of stereotypes attributes.

        The method does nothing at the moment. In the future it should
        probably display stereotypes attributes under stereotypes header.

        Abstract class for classifiers overrides this method to display
        stereotypes attributes in compartments.
        """
        pass

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
        # by default no stereotype, however check for __stereotype__
        # attribute to assign some static stereotype see interfaces,
        # use case relationships, package or class for examples
        stereotype = getattr(self, '__stereotype__', ())
        if stereotype:
            stereotype = self.parse_stereotype(stereotype)

        # Phew! :] :P
        stereotype = modelfactory.stereotypes_str(self.subject, stereotype)
        self.set_stereotype(stereotype)

    def parse_stereotype(self, data):
        if isinstance(data, str):  # return data as stereotype if it is a string
            return (data,)

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
                ok = type(subject) is cls  # isinstance(subject, cls)
            if predicate:
                ok = predicate(self)

            if ok:
                return (stereotype,)
        return ()


class DiagramItem(six.with_metaclass(DiagramItemMeta, uml2.Presentation, StereotypeSupport, EditableTextSupport)):
    """
    Basic functionality for all model elements (lines and elements!).

    This class contains common functionallity for model elements and
    relationships.
    It provides an interface similar to uml2.Element for connecting and
    disconnecting signals.

    This class is not very useful on its own. It contains some glue-code for
    diacanvas.DiaCanvasItem and gaphor.UML.uml2.Element.

    Example:
        class ElementItem(diacanvas.CanvasElement, DiagramItem):
            connect = DiagramItem.connect
            disconnect = DiagramItem.disconnect
            ...

    @cvar style: styles information (derived from DiagramItemMeta)
    """

    dispatcher = inject('element_dispatcher')

    def __init__(self, id=None):
        uml2.Presentation.__init__(self)
        EditableTextSupport.__init__(self)
        StereotypeSupport.__init__(self)

        self._id = id

        # properties, which should be saved in file
        self._persistent_props = set()

        def update(event):
            self.request_update()

        self.watcher = EventWatcher(self, default_handler=update)

        self.watch('subject') \
            .watch('subject.appliedStereotype.classifier.name', self.on_element_applied_stereotype)

    id = property(lambda self: self._id, doc='Id')

    def set_prop_persistent(self, name):
        """
        Specify property of diagram item, which should be saved in file.
        """
        self._persistent_props.add(name)

    # TODO: Use adapters for load/save functionality
    def save(self, save_func):
        if self.subject:
            save_func('subject', self.subject)

        save_func('show_stereotypes_attrs', self.show_stereotypes_attrs)

        # save persistent properties
        for p in self._persistent_props:
            save_func(p, getattr(self, p.replace('-', '_')))

    def load(self, name, value):
        if name == 'subject':
            type(self).subject.load(self, value)
        elif name == 'show_stereotypes_attrs':
            self._show_stereotypes_attrs = eval(value)
        else:
            try:
                setattr(self, name.replace('-', '_'), eval(value))
            except:
                logger.warning('%s has no property named %s (value %s)' % \
                               (self, name, value))

    def postload(self):
        if self.subject:
            self.update_stereotype()
            self.update_stereotypes_attrs()

    def save_property(self, save_func, name):
        """
        Save a property, this is a shorthand method.
        """
        save_func(name, getattr(self, name.replace('-', '_')))

    def save_properties(self, save_func, *names):
        """
        Save a property, this is a shorthand method.
        """
        for name in names:
            self.save_property(save_func, name)

    def unlink(self):
        """
        Remove the item from the canvas and set subject to None.
        """
        if self.canvas:
            self.canvas.remove(self)
        super(DiagramItem, self).unlink()

    def request_update(self):
        """
        Placeholder for gaphor.Item's request_update() method.
        """
        pass

    def pre_update(self, context):
        EditableTextSupport.pre_update(self, context)

    def post_update(self, context):
        EditableTextSupport.post_update(self, context)

    def draw(self, context):
        EditableTextSupport.draw(self, context)

    def item_at(self, x, y):
        return self

    def on_element_applied_stereotype(self, event):
        if self.subject:
            self.update_stereotype()
            self.request_update()

    def watch(self, path, handler=None):
        """
        Watch a certain path of elements starting with the DiagramItem.
        The handler is optional and will default to a simple
        self.request_update().
        
        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        self.watcher.watch(path, handler)
        return self

    def register_handlers(self):
        self.watcher.register_handlers()

    def unregister_handlers(self):
        self.watcher.unregister_handlers()

# vim:sw=4:et:ai
