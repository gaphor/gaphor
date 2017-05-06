#!/usr/bin/env python

# This is Gaphor, a Python+GTK modeling tool

# Copyright 2007, 2008, 2011 Arjan Molenaar, 2017 Dan Yeaw

# Gaphor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Gaphor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.

"""
The Core module provides an entry point for Gaphor's core constructs.

An average module should only need to import this module.
"""

from __future__ import absolute_import
from gaphor.application import inject, Application
from gaphor.transaction import Transaction, transactional
from gaphor.action import action, toggle_action, radio_action, open_action, build_action_group
from gaphor.i18n import _

# vim:sw=4:et:ai
