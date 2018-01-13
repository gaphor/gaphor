#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Use cases related connection adapters.
"""

from __future__ import absolute_import
from zope import component
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.adapters.connectors import RelationshipConnect


class IncludeConnect(RelationshipConnect):
    """
    Connect use cases with an include item relationship.
    """
    component.adapts(items.UseCaseItem, items.IncludeItem)

    def allow(self, handle, port):
        line = self.line
        element = self.element

        if not (element.subject and isinstance(element.subject, uml2.UseCase)):
            return None

        return super(IncludeConnect, self).allow(handle, port)


    def reconnect(self, handle, port):
        self.reconnect_relationship(handle, uml2.Include.addition, uml2.Include.includingCase)


    def connect_subject(self, handle):
        relation = self.relationship_or_new(uml2.Include,
                    uml2.Include.addition,
                    uml2.Include.includingCase)
        self.line.subject = relation

component.provideAdapter(IncludeConnect)


class ExtendConnect(RelationshipConnect):
    """
    Connect use cases with an extend item relationship.
    """
    component.adapts(items.UseCaseItem, items.ExtendItem)

    def allow(self, handle, port):
        line = self.line
        element = self.element
        
        if not (element.subject and isinstance(element.subject, uml2.UseCase)):
            return None

        return super(ExtendConnect, self).allow(handle, port)

    def reconnect(self, handle, port):
        self.reconnect_relationship(handle, uml2.Extend.extendedCase, uml2.Extend.extension)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(uml2.Extend,
                    uml2.Extend.extendedCase,
                    uml2.Extend.extension)
        self.line.subject = relation

component.provideAdapter(ExtendConnect)

# vim:sw=4:et:ai

