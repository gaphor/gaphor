#!/usr/bin/env python

# Copyright (C) 2001-2017 Arjan Molenaar <gaphor@gmail.com>
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
This module contains user interface related code, such as the
main screen and diagram windows.
"""

from __future__ import absolute_import
import gtk
import pkg_resources
import os.path

icon_theme = gtk.icon_theme_get_default()
icon_theme.append_search_path(os.path.abspath(
                                pkg_resources.resource_filename('gaphor.ui', 'pixmaps')))

import re
def _repl(m):
    v = m.group(1).lower()
    return len(v) == 1 and v or '%c-%c' % tuple(v)


_repl.expr = '(.?[A-Z])'


def icon_for_element(element):
    return re.sub(_repl.expr, _repl, type(element).__name__)

# vim:sw=4:et:
