#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
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
Plugin based on the Live Object browser
(http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/300304).
It shows the state of the data model at the time the browser is activated.
"""

from __future__ import absolute_import
from zope import interface
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider
from .browser import Browser


class LiveObjectBrowser(object):

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="tools">
            <menuitem action="tools-life-object-browser" />
          </menu>
        </menubar>
      </ui>"""

    def __init__(self):
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    @action(name='tools-life-object-browser', label='Life object browser')
    def execute(self):
        browser = Browser("resource", self.element_factory.lselect())


# vim:sw=4:et
