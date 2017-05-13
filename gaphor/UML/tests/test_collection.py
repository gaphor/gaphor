#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test if the collection's list supports all trickery.
"""

from __future__ import absolute_import
import unittest
from gaphor.UML.collection import collectionlist

class CollectionlistTestCase(unittest.TestCase):

    def test_listing(self):
        c = collectionlist()
        c.append('a')
        c.append('b')
        c.append('c')
        assert str(c) == "['a', 'b', 'c']"

# vim:sw=4:et:ai
