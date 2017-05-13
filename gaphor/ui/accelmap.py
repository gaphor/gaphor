#!/usr/bin/env python

# Copyright (C) 2001-2017 Adam Boduch <adam.boduch@gmail.com>
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
"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

from __future__ import absolute_import
import os, os.path
import gtk

from gaphor.misc import get_user_data_dir

def _get_accel_map_filename():
    """
    The Gaphor accelMap file ($HOME/.gaphor/accelmap).
    """
    
    user_data_dir = get_user_data_dir()
    
    if not os.path.exists(user_data_dir):
        os.mkdir(user_data_dir)
    return os.path.join(user_data_dir, 'accelmap')


def load_accel_map():
    """
    Load the user accelerator map from the gaphor user home directory
    """
    filename = _get_accel_map_filename()
    if os.path.exists(filename) and os.path.isfile(filename):
        gtk.accel_map_load(filename)


def save_accel_map():
    """
    Save the contents of the GtkAccelMap to a file.
    """
    filename = _get_accel_map_filename()
    gtk.accel_map_save(filename)   


# vim:sw=4:et:
