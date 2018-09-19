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
"""This module defines two visualization items - OperationItem and ClassItem."""

from __future__ import absolute_import
from gaphas.state import observed, reversible_property

from gaphor.UML import uml2

from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.compartment import FeatureItem

class OperationItem(FeatureItem):
    """This is visualization of a class operation and is a type of
    FeatureItem."""

    def render(self):
        """Render the OperationItem."""
        
        return '{}'.format(self.subject) or ''
        
class ClassItem(ClassifierItem):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments (Compartment): one for
    attributes and one for operations. To add and remove such features
    the ClassItem implements the CanvasGroupable interface.
    Items can be added by callling class.add() and class.remove().
    This is used to handle CanvasItems, not UML objects!"""

    __uml__ = uml2.Class, uml2.Stereotype
    
    __stereotype__ = {
        'stereotype': uml2.Stereotype,
        'metaclass': lambda self: (not isinstance(self.subject, uml2.Stereotype)) and hasattr(self.subject, 'extension') and self.subject.extension,
    }
    
    __style__ = {
        'extra-space': 'compartment',
        'abstract-feature-font': 'sans italic 10',
    }

    def __init__(self, id=None):
        """Constructor.  Initialize the ClassItem.  This will also call the
        ClassifierItem constructor.
        
        The drawing style is set here as well.  The class item will create
        two compartments - one for attributes and another for operations."""
        
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self._attributes = self.create_compartment('attributes')
	self._attributes.font = self.style.feature_font
        self._operations = self.create_compartment('operations')
	self._operations.font = self.style.feature_font
        self._operations.use_extra_space = True

        self.watch('subject<Class>.ownedOperation', self.on_class_owned_operation)\
            .watch('subject<Class>.ownedAttribute.association', self.on_class_owned_attribute) \
            .watch('subject<Class>.ownedAttribute.name') \
            .watch('subject<Class>.ownedAttribute.isStatic') \
            .watch('subject<Class>.ownedAttribute.isDerived') \
            .watch('subject<Class>.ownedAttribute.visibility') \
            .watch('subject<Class>.ownedAttribute.lowerValue') \
            .watch('subject<Class>.ownedAttribute.upperValue') \
            .watch('subject<Class>.ownedAttribute.defaultValue') \
            .watch('subject<Class>.ownedAttribute.typeValue') \
            .watch('subject<Class>.ownedOperation.name') \
            .watch('subject<Class>.ownedOperation.isAbstract', self.on_operation_is_abstract) \
            .watch('subject<Class>.ownedOperation.isStatic') \
            .watch('subject<Class>.ownedOperation.visibility') \
            .watch('subject<Class>.ownedOperation.returnResult.lowerValue') \
            .watch('subject<Class>.ownedOperation.returnResult.upperValue') \
            .watch('subject<Class>.ownedOperation.returnResult.typeValue') \
            .watch('subject<Class>.ownedOperation.formalParameter.lowerValue') \
            .watch('subject<Class>.ownedOperation.formalParameter.upperValue') \
            .watch('subject<Class>.ownedOperation.formalParameter.typeValue') \
            .watch('subject<Class>.ownedOperation.formalParameter.defaultValue')

    def save(self, save_func):
        """Store the show- properties *before* the width/height properties,
        otherwise the classes will unintentionally grow due to "visible"
        attributes or operations."""
        
        self.save_property(save_func, 'show-attributes')
        self.save_property(save_func, 'show-operations')
        ClassifierItem.save(self, save_func)

    def postload(self):
        """Called once the ClassItem has been loaded.  First the ClassifierItem
        is "post-loaded", then the attributes and operations are
        synchronized."""
        super(ClassItem, self).postload()
        self.sync_attributes()
        self.sync_operations()

    @observed
    def _set_show_operations(self, value):
        """Sets the show operations property.  This will either show or hide
        the operations compartment of the ClassItem.  This is part of the
        show_operations property."""
        
        self._operations.visible = value
        self._operations.use_extra_space = value
        self._attributes.use_extra_space = not self._operations.visible

    show_operations = reversible_property(fget=lambda s: s._operations.visible,
            fset=_set_show_operations)
    
    @observed
    def _set_show_attributes(self, value):
        """Sets the show attributes property.  This will either show or hide
        the attributes compartment of the ClassItem.  This is part of the
        show_attributes property."""
        
        self._attributes.visible = value

    show_attributes = reversible_property(fget=lambda s: s._attributes.visible,
                               fset=_set_show_attributes)

    def _create_attribute(self, attribute):
        """Create a new attribute item.  This will create a new FeatureItem
        and assigns the specified attribute as the subject."""
        
        new = FeatureItem()
        new.subject = attribute
        new.font = self.style.feature_font
        
        self._attributes.append(new)


    def _create_operation(self, operation):
        """Create a new operation item.  This will create a new OperationItem
        and assigns the specified operation as the subject."""
        
        new = OperationItem()
        new.subject = operation
        new.font = self.style.feature_font
        
        self._operations.append(new)

    def sync_attributes(self):
        """Sync the contents of the attributes compartment with the data
        in self.subject."""
        
        owned_attributes = [a for a in self.subject.ownedAttribute if not a.association]
        self.sync_uml_elements(owned_attributes,\
                               self._attributes,\
                               self._create_attribute)

    def sync_operations(self):
        """Sync the contents of the operations compartment with the data
        in self.subject."""
        
        self.sync_uml_elements(self.subject.ownedOperation,\
                               self._operations,\
                               self._create_operation)

    def on_class_owned_attribute(self, event):
        """Event handler for owned attributes.  This will synchronize the
        attributes of this ClassItem."""
        
        if self.subject:
            self.sync_attributes()

    def on_class_owned_operation(self, event):
        """Event handler for owned operations.  This will synchronize the
        operations of this ClassItem."""
        
        if self.subject:
            self.sync_operations()

    def on_operation_is_abstract(self, event):
        """Event handler for abstract operations.  This will change the font
        of the operation."""
        
        o = [o for o in self._operations if o.subject is event.element]
        if o:
            o = o[0]
            o.font = (o.subject and o.subject.isAbstract) \
                    and self.style.abstract_feature_font or self.style.feature_font
            self.request_update()
