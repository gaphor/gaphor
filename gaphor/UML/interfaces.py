#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
UML events emited on a change in the data model.
"""

from __future__ import absolute_import
from zope import interface
from gaphor.interfaces import IServiceEvent

class IElementEvent(interface.Interface):
    """Generic event fired when element state changes.
    """
    element = interface.Attribute("The changed element")


class IElementCreateEvent(IElementEvent):
    """A new element has been created.
    """


class IElementDeleteEvent(IElementEvent):
    """An element is deleted from the model.
    """


class IElementChangeEvent(IElementEvent):
    """
    Generic event fired when element state changes.
    """
    property = interface.Attribute("The property that changed")
    old_value = interface.Attribute("The property value before the change")
    new_value = interface.Attribute("The property value after the change")


class IAttributeChangeEvent(IElementChangeEvent):
    """
    An attribute has changed.
    """


class IAssociationChangeEvent(IElementChangeEvent):
    """
    An association hs changed.
    This event may be fired for both ends of the association.
    """

class IAssociationSetEvent(IAssociationChangeEvent):
    """
    An association with [0..1] multiplicity has been changed.
    """

class IAssociationAddEvent(IAssociationChangeEvent):
    """
    An association with [0..*] multiplicity has been changed: a new entry is
    added. ``new_value`` contains the property being added.
    """

class IAssociationDeleteEvent(IAssociationChangeEvent):
    """
    An association with [0..*] multiplicity has been changed: an entry has
    been removed. ``old_value`` contains the property that has been removed.
    """

class IElementFactoryEvent(IServiceEvent):
    """
    Events related to individual model elements.
    """

class IModelFactoryEvent(IElementFactoryEvent):
    """
    A new model is loaded into the ElementFactory.
    """


class IFlushFactoryEvent(IElementFactoryEvent):
    """
    All elements are removed from the ElementFactory.
    This event is emitted before the factory is emptied.
    """


# vim: sw=4:et
