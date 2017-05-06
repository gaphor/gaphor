#!/usr/bin/env python

# This is Gaphor, a Python+GTK modeling tool

# Copyright 2007, Arjan Molenaar, 2017 Dan Yeaw

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

"""Test for actions in generic files."""

from __future__ import absolute_import
import doctest
from gaphor import action


def test_suite():
    return doctest.DocTestSuite(action)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')

# vim:sw=4:et:ai
