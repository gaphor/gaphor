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
Plugins
=======

This module contains a bunch of standard plugins.
Plugins can be registered in Gaphor by declaring them as service entry point::

    entry_points = {
        'gaphor.services': [
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
        ],
    },


There is a thin line between a service and a plugin. A service typically performs some basic need for the applications (such as the element factory or the undo mechanism). A plugin is more of an add-on. For example a plugin can depend on external libraries or provide a cross-over function between two applications.

"""

