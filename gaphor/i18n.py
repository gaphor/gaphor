#!/usr/bin/env python

# Copyright (C) 2003-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import

import gettext
import os

import pkg_resources

__all__ = ['_']

localedir = os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'data', 'locale')

try:

    catalog = gettext.Catalog('gaphor', localedir=localedir)
    _ = catalog.gettext

except IOError as e:

    def _(s):
        return s
