#!/usr/bin/env python

# Copyright (C) 2001-2017 Arjan Molenaar <gaphor@gmail.com>
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
Package gaphor.diagram.states implements diagram items for UML state machines.

Pseudostates
============
There are some similarities between activities and state machines, for example
    - initial node and initial psuedostate
    - final node and final state
Of course, they differ in many aspects, but the similarites drive user
interface of state machines. This is with respect of minimalization of the set
of diagram items (i.e. there is only one diagram item for both join and fork
nodes in activities implemented in Gaphor).

There are separate diagram items for pseudostates
    - initial pseudostate item as there exists initial node item

@todo: Probably, history pseudostates will be implemented as one diagram item
    with an option deep/shallow. [This section is going to be extended as
    we start to implement more pseudostates].
"""

from __future__ import absolute_import
from gaphor.diagram.nameditem import NamedItem

class VertexItem(NamedItem):
    """
    Abstract class for all vertices. All state, pseudostate items derive
    from VertexItem, which simplifies transition connection adapters.
    """
    pass

