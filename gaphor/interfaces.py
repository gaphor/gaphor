#!/usr/bin/env python

# Copyright (C) 2005-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#                         slmm <noreply@example.com>
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
from __future__ import absolute_import

from zope import interface


class IService(interface.Interface):
    """
    Base interface for all services in Gaphor.
    """

    def init(self, application):
        """
        Initialize the service, this method is called after all services
        are instantiated.
        """

    def shutdown(self):
        """
        Shutdown the services, free resources.
        """


class IServiceEvent(interface.Interface):
    """
    An event emitted by a service.
    """
    service = interface.Attribute("The service that emits the event")


class ITransaction(interface.Interface):
    """
    The methods each transaction should adhere.
    """

    def commit(self):
        """
        Commit the transaction.
        """

    def rollback(self):
        """
        Roll back the transaction.
        """


class ITransactionEvent(interface.Interface):
    """
    Events related to transaction workflow (begin/commit/rollback) implements
    this interface.
    """


class IActionProvider(interface.Interface):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py) and the accompanying XML for the UI manager.
    """
    menu_xml = interface.Attribute("The menu XML")

    action_group = interface.Attribute("The accompanying ActionGroup")


class IActionExecutedEvent(interface.Interface):
    """
    An event emited when an action has been performed.
    """
    name = interface.Attribute("Name of the action performed, if any")

    action = interface.Attribute("The performed action")


class IEventFilter(interface.Interface):
    """
    Filter events when they're about to be handled.
    """

    def filter(self):
        """
        Return a value (e.g. message/reason) why the event is filtered.
        Returning `None` or `False` will propagate the event.
        """

# vim:sw=4:et
