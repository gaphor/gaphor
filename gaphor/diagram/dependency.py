'''
Dependency -- 
'''
# vim:sw=4:et

from __future__ import generators

import math
import gobject
import pango
import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.diagram import initialize_item

from relationship import RelationshipItem

STEREOTYPE_OPEN = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class DependencyItem(RelationshipItem):
    """This class represents all types of dependencies.

    Normally a dependency looks like a dashed line woth an arrow head.
    The dependency can have a stereotype attached to it, stating the kind of
    dependency we're dealing with. The dependency kind can only be changed if
    the dependency is not connected to two items.

    In the special case of an Usage dependency, where one end is
    connected to an InterfaceItem: the line is drawn as a solid line without
    arrowhead.  The Interface will draw a half a circle on the side where the
    Usage dep. is connected.

    Although it is possible to add multiple Implementation and Usage
    dependencies to an interface, it will probably not be very explaining
    (esp. Usage dependencies).

    TODO (see also InterfaceItem): When a Usage dependency is drawn and is
          connected to an InterfaceItem, draw a solid line, but stop drawing
          the line 'x' points before the last handle.
    """

    FONT = 'sans 10'

    dependency_popup_menu = (
	'separator',
	'Dependency type', (
            'AutoDependency',
            'separator',
	    'DependencyTypeDependency',
	    'DependencyTypeUsage',
	    'DependencyTypeRealization')
    )

    def __init__(self, id=None):
	self.dependency_type = UML.Dependency
        self.auto_dependency = True

        RelationshipItem.__init__(self, id)

        font = pango.FontDescription(self.FONT)
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(font)
        self._stereotype.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)

        self.set(head_fill_color=0, head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
        self._set_line_style()

    def save(self, save_func):
	RelationshipItem.save(self, save_func)
	save_func('dependency_type', self.dependency_type.__name__)
        save_func('auto_dependency', self.auto_dependency)

    def load(self, name, value):
	if name == 'dependency_type':
	    self.set_dependency_type(getattr(UML, value))
        elif name == 'auto_dependency':
            self.auto_dependency = eval(value)
	else:
	    RelationshipItem.load(self, name, value)

    def get_popup_menu(self):
        if self.subject:
            return self.popup_menu
        else:
            return self.popup_menu + self.dependency_popup_menu

    def get_dependency_type(self):
	return self.dependency_type

    def set_dependency_type(self, dependency_type):
	self.dependency_type = dependency_type
        self._set_line_style()

    def _set_line_style(self, c1=None):
        """Display a depenency as a dashed arrow, with optional stereotype.
        """
        from interface import InterfaceItem
        dependency_type = self.dependency_type
        c1 = c1 or self.handles[0].connected_to
        if c1 and self.dependency_type is UML.Usage and isinstance(c1, InterfaceItem) and c1.is_folded():
            if self.get_property('has_head'):
                self.set(dash=None, has_head=0)
            self._stereotype.set_text('')
        else:
            if not self.get_property('has_head'):
                self.set(dash=(7.0, 5.0), has_head=1)
            if dependency_type is UML.Usage:
                self._stereotype.set_text(STEREOTYPE_OPEN + 'use' + STEREOTYPE_CLOSE)
            elif dependency_type is UML.Realization:
                self._stereotype.set_text(STEREOTYPE_OPEN + 'realize' + STEREOTYPE_CLOSE)
            elif dependency_type is UML.Implementation:
                self._stereotype.set_text(STEREOTYPE_OPEN + 'implements' + STEREOTYPE_CLOSE)
            else:
                self._stereotype.set_text('')

    def update_label(self, p1, p2):
        w, h = self._stereotype.to_pango_layout(True).get_pixel_size()

        x = p1[0] > p2[0] and w + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and h or 0
        y = (p1[1] + p2[1]) / 2.0 - y

	self._stereotype.set_pos((x, y))

	return x, y, w, h

    def on_update (self, affine):
        self._set_line_style();
        RelationshipItem.on_update(self, affine)
        handles = self.handles
        middle = len(handles)/2
        b1 = self.update_label(handles[middle-1].get_pos_i(),
                                 handles[middle].get_pos_i())

        b2 = self.bounds
        self.set_bounds((min(b1[0], b2[0]), min(b1[1], b2[1]),
                         max(b1[2] + b1[0], b2[2]), max(b1[3] + b1[1], b2[3])))

    def on_shape_iter(self):
	for s in RelationshipItem.on_shape_iter(self):
	    yield s
	yield self._stereotype

    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        return self._find_relationship(head_subject, tail_subject,
                                       ('supplier', 'supplierDependency'),
                                       ('client', 'clientDependency'))

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.NamedElement)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().

        In case of an Implementation, the head should be connected to an
        Interface and the tail to a BehavioredClassifier.

        TODO: Should Class also inherit from BehavioredClassifier?
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
        self._set_line_style(c1)

        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                relation = gaphor.resource(UML.ElementFactory).create(self.dependency_type)
                relation.supplier = s1
                relation.client = s2
            self.subject = relation
        if self.auto_dependency:
            # Determine the dependency_type if only one handle is connected
            #from interface import InterfaceItem
            if c1 and isinstance(c1.subject, UML.Interface):
                self.set_dependency_type(UML.Usage)
            else:
                self.set_dependency_type(UML.Dependency)

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        self._set_line_style()
        self.set_subject(None)

initialize_item(DependencyItem, UML.Dependency)
