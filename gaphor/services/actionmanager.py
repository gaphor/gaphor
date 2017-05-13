#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import

import gtk
from logging import getLogger
from zope import interface, component

from gaphor.core import inject
from gaphor.event import ServiceInitializedEvent, ActionExecuted
from gaphor.interfaces import IService, IActionProvider


class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    interface.implements(IService)
    logger = getLogger('ActionManager')

    component_registry = inject('component_registry')

    ui_manager = inject('ui_manager')

    def __init__(self):
        pass

    def init(self, app):
        self.logger.info('Loading action provider services')

        for name, service in self.component_registry.get_utilities(IActionProvider):
            self.logger.debug('Service is %s' % service)
            self.register_action_provider(service)

        self.component_registry.register_handler(self._service_initialized_handler)

    def shutdown(self):

        self.logger.info('Shutting down')

        self.component_registry.unregister_handler(self._service_initialized_handler)

    def execute(self, action_id, active=None):

        self.logger.debug('Executing action, action_id is %s' % action_id)

        a = self.get_action(action_id)
        if a:
            a.activate()
            self.component_registry.handle(ActionExecuted(action_id, a))
        else:
            self.logger.warning('Unknown action %s' % action_id)

    def update_actions(self):

        self.ui_manager.ensure_update()

    def get_action(self, action_id):

        for g in self.ui_manager.get_action_groups():
            a = g.get_action(action_id)
            if a: return a

    def register_action_provider(self, action_provider):

        self.logger.debug('Registering action provider %s' % action_provider)

        action_provider = IActionProvider(action_provider)

        try:
            # Check if the action provider is not already registered
            action_provider.__ui_merge_id
        except AttributeError:
            assert action_provider.action_group
            self.ui_manager.insert_action_group(action_provider.action_group, -1)

            try:
                menu_xml = action_provider.menu_xml
            except AttributeError:
                pass
            else:
                action_provider.__ui_merge_id = \
                    self.ui_manager.add_ui_from_string(menu_xml)

    @component.adapter(ServiceInitializedEvent)
    def _service_initialized_handler(self, event):

        self.logger.debug('Handling ServiceInitializedEvent')
        self.logger.debug('Service is %s' % event.service)

        if IActionProvider.providedBy(event.service):
            self.logger.debug('Loading registered service %s' % event.service)

            self.register_action_provider(event.service)


class UIManager(gtk.UIManager):
    """
    Service version of gtk.UIManager.
    """

    interface.implements(IService)

    def init(self, app=None):
        pass

    def shutdown(self):
        pass

# vim:sw=4:et:ai
