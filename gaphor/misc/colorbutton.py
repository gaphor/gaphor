#!/usr/bin/env python

# Copyright (C) 2010-2017 Arjan Molenaar <gaphor@gmail.com>
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
A version of the standard gtk.ColorButton tweaked towards Gaphor.

Gaphor is using color values from 0 to 1 (cairo standard), so that required some tweaks
on the color widget. The standard format is `(red, green, blue, alpha)`.
"""

from __future__ import absolute_import
import gtk


class ColorButton(gtk.ColorButton):

    __gtype_name__ = 'GaphorColorButton'

    def __init__(self, r, g, b, a):
        gtk.Button.__init__(self)
        self.set_color(gtk.gdk.Color(int(r * 65535),
                                     int(g * 65535),
                                     int(b * 65535)))
        self.set_use_alpha(True)
        self.set_alpha(int(a * 65535))

    def get_color_float(self):
        c = self.get_color()
        return (c.red_float, c.green_float, c.blue_float, self.get_alpha() / 65535.)

    color = property(lambda s: s.get_color_float())

# vim:sw=4:et:ai
