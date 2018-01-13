#!/usr/bin/env python

# Copyright (C) 2002-2017 Adam Boduch <adam.boduch@gmail.com>
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
"""Provides a get_user_data_dir() function for retrieving the user's data
directory."""

from __future__ import absolute_import
import os

def get_user_data_dir():
    
    """Return the directory where the user's data is stored.  This varies
    depending on platform."""
    
    if os.name == 'nt':
        home = 'USERPROFILE'
    else:
        home = 'HOME'

    return os.path.join(os.getenv(home), '.gaphor')
