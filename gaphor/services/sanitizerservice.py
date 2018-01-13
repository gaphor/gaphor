#!/usr/bin/env python

# Copyright (C) 2008-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
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
The Sanitize module is dedicated to adapters (stuff) that keeps
the model clean and in sync with diagrams.
"""

from __future__ import absolute_import
from zope import interface
from zope import component

from logging import getLogger
from gaphor.UML import uml2, modelfactory
from gaphor.UML.interfaces import IAssociationDeleteEvent, IAssociationSetEvent
from gaphor.interfaces import IService
from gaphor.core import inject

class SanitizerService(object):
    """
    Does some background cleanup jobs, such as removing elements from the
    model that have no presentations (and should have some).
    """
    interface.implements(IService)

    logger = getLogger('Sanitizer')

    component_registry = inject('component_registry')
    element_factory = inject('element_factory')
    property_dispatcher = inject('property_dispatcher')

    def __init__(self):
        pass

    def init(self, app=None):
        self.component_registry.register_handler(self._unlink_on_presentation_delete)
        self.component_registry.register_handler(self._unlink_on_stereotype_delete)
        self.component_registry.register_handler(self._unlink_on_extension_delete)
        self.component_registry.register_handler(self._disconnect_extension_end)

    def shutdown(self):
        self.component_registry.unregister_handler(self._unlink_on_presentation_delete)
        self.component_registry.unregister_handler(self._unlink_on_stereotype_delete)
        self.component_registry.unregister_handler(self._unlink_on_extension_delete)
        self.component_registry.unregister_handler(self._disconnect_extension_end)
        

    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_presentation_delete(self, event):
        """
        Unlink the model element if no more presentations link to the `item`'s
        subject or the deleted item was the only item currently linked.
        """
        
        self.logger.debug('Handling IAssociationDeleteEvent')
        #self.logger.debug('Property is %s' % event.property.name)
        #self.logger.debug('Element is %s' % event.element)
        #self.logger.debug('Old value is %s' % event.old_value)
        
        if event.property is uml2.Element.presentation:
            old_presentation = event.old_value
            if old_presentation and not event.element.presentation:
                event.element.unlink()

    def perform_unlink_for_instances(self, st, meta):
        
        self.logger.debug('Performing unlink for instances')
        #self.logger.debug('Stereotype is %s' % st)
        #self.logger.debug('Meta is %s' % meta)
                
        inst = modelfactory.find_instances(self.element_factory, st)

        for i in list(inst):
            for e in i.extended:
                if not meta or isinstance(e, meta):
                    i.unlink()


    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_extension_delete(self, event):
        """
        Remove applied stereotypes when extension is deleted.
        """
        
        self.logger.debug('Handling IAssociationDeleteEvent')
        #self.logger.debug('Property is %s' % event.property.name)
        #self.logger.debug('Element is %s' % event.element)
        #self.logger.debug('Old value is %s' % event.old_value)
        
        if isinstance(event.element, uml2.Extension) and \
                event.property is uml2.Association.memberEnd and \
                event.element.memberEnd:
            p = event.element.memberEnd[0]
            ext = event.old_value
            if isinstance(p, uml2.ExtensionEnd):
                p, ext = ext, p
            st = ext.type
            meta = p.type and getattr(uml2, p.type.name)
            self.perform_unlink_for_instances(st, meta)


    @component.adapter(IAssociationSetEvent)
    def _disconnect_extension_end(self, event):
        
        self.logger.debug('Handling IAssociationSetEvent')
        #self.logger.debug('Property is %s' % event.property.name)
        #self.logger.debug('Element is %s' % event.element)
        #self.logger.debug('Old value is %s' % event.old_value)
        
        if event.property is uml2.ExtensionEnd.type and event.old_value:
            ext = event.element
            p = ext.opposite
            if not p:
                return
            st = event.old_value
            meta = getattr(uml2, p.type.name)
            self.perform_unlink_for_instances(st, meta)


    @component.adapter(IAssociationDeleteEvent)
    def _unlink_on_stereotype_delete(self, event):
        """
        Remove applied stereotypes when stereotype is deleted.
        """
        
        self.logger.debug('Handling IAssociationDeleteEvent')
        #self.logger.debug('Property is %s' % event.property)
        #self.logger.debug('Element is %s' % event.element)
        #self.logger.debug('Old value is %s' % event.old_value)
        
        if event.property is uml2.InstanceSpecification.classifier:
            if isinstance(event.old_value, uml2.Stereotype):
                event.element.unlink()


# vim:sw=4:et:ai
