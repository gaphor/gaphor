'''
Dependency -- 
'''
# vim:sw=4

from __future__ import generators

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

    FONT = 'sans 10'

    dependency_popup_menu = (
	'separator',
	'Dependency type', (
	    'DependencyTypeDependency',
	    'DependencyTypeUsage',
	    'DependencyTypeRealization')
    )

    def __init__(self, id=None):
	self.dependency_type = UML.Dependency

        RelationshipItem.__init__(self, id)
        self.set(dash=(7.0, 5.0), has_head=1, head_fill_color=0,
                 head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
        
        font = pango.FontDescription(self.FONT)
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(font)
        self._stereotype.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)

    def get_popup_menu(self):
        if self.subject:
            return self.popup_menu
        else:
            return self.popup_menu + self.dependency_popup_menu

    def get_dependency_type(self):
	return self.dependency_type

    def set_dependency_type(self, dependency_type):
	self.dependency_type = dependency_type

	if dependency_type is UML.Usage:
	    self._stereotype.set_text(STEREOTYPE_OPEN + 'use' + STEREOTYPE_CLOSE)
	elif dependency_type is UML.Realization:
	    self._stereotype.set_text(STEREOTYPE_OPEN + 'realize' + STEREOTYPE_CLOSE)
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

        for supplier in head_subject.supplierDependency:
            #print 'supplier', supplier, supplier.client, tail_subject
            if tail_subject in supplier.client:
                # Check if the dependency is not already in our diagram
                for item in supplier.presentation:
                    if item.canvas is self.canvas and item is not self:
                        break
                else:
                    return supplier

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.NamedElement)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
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

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        if self.subject:
            del self.subject

initialize_item(DependencyItem, UML.Dependency)
