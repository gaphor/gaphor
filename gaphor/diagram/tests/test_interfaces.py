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
Test Interfaces.
"""

from __future__ import absolute_import
from gaphor import diagram
from gaphor.tests import TestCase


class InterfacesTestCase(TestCase):

    def test_comment(self):
        #self.assertTrue(diagram.interfaces.ICommentItem.implementedBy(diagram.comment.CommentItem))
        item = diagram.comment.CommentItem()
        editor = diagram.interfaces.IEditor(item)
        self.assertTrue(editor)
        self.assertTrue(editor._item is item)
        

# vim: sw=4:et
