#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Connection between two state machine vertices (state, pseudostate) using
transition.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import absolute_import
from zope import component
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.adapters.connectors import RelationshipConnect


class VertexConnect(RelationshipConnect):
    """
    Abstract relationship between two state vertices.
    """

    def reconnect(self, handle, port):
        self.reconnect_relationship(handle, uml2.Transition.source, uml2.Transition.target)


    def connect_subject(self, handle):
        relation = self.relationship_or_new(uml2.Transition,
                    uml2.Transition.source,
                    uml2.Transition.target)
        self.line.subject = relation
        if relation.guard is None:
            relation.guard = self.element_factory.create(uml2.Constraint)



class TransitionConnect(VertexConnect):
    """
    Connect two state vertices using transition item.
    """
    component.adapts(items.VertexItem, items.TransitionItem)

    def allow(self, handle, port):
        """
        Glue transition handle and vertex item. Guard from connecting
        transition's head with final state.
        """
        line = self.line
        subject = self.element.subject

        is_final = isinstance(subject, uml2.FinalState)
        if isinstance(subject, uml2.State) and not is_final \
                or handle is line.tail and is_final:
            return super(TransitionConnect, self).allow(handle, port)
        else:
            return None

component.provideAdapter(TransitionConnect)


class InitialPseudostateTransitionConnect(VertexConnect):
    """
    Connect initial pseudostate using transition item.

    It modifies InitialPseudostateItem._connected attribute to disallow
    connection of more than one transition.
    """
    component.adapts(items.InitialPseudostateItem, items.TransitionItem)

    def allow(self, handle, port):
        """
        Glue to initial pseudostate with transition's head and when there are
        no transitions connected.
        """
        line = self.line
        element = self.element
        subject = element.subject

        # Check if no other items are connected
        connections = self.canvas.get_connections(connected=element)
        connected_items = [c for c in connections if isinstance(c.item, items.TransitionItem) and c.item is not line]
        if handle is line.head and not any(connected_items):
            return super(InitialPseudostateTransitionConnect, self).allow(handle, port)
        else:
            return None

component.provideAdapter(InitialPseudostateTransitionConnect)

class HistoryPseudostateTransitionConnect(VertexConnect):
    """
    Connect history pseudostate using transition item.

    It modifies InitialPseudostateItem._connected attribute to disallow
    connection of more than one transition.
    """
    component.adapts(items.HistoryPseudostateItem, items.TransitionItem)

    def allow(self, handle, port):
        """
        """
        return super(HistoryPseudostateTransitionConnect, self).allow(handle, port)

component.provideAdapter(HistoryPseudostateTransitionConnect)

# vim:sw=4:et:ai
