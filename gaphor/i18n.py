#!/usr/bin/env python

# This is Gaphor, a Python+GTK modeling tool

# Copyright 2003, 2004, 2007, 2011 Arjan Molenaar, 2017 Dan Yeaw

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

"""Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language."""

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
