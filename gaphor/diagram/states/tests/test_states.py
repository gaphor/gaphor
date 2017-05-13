#!/usr/bin/env python

# Copyright (C) 2010-2017 Artur Wroblewski <wrobell@pld-linux.org>
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
Test state items.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.states.state import StateItem
from gaphor.tests.testcase import TestCase


class StateTestCase(TestCase):
    def test_state(self):
        """Test creation of states
        """
        self.create(StateItem, uml2.State)


    def test_activities_persistence(self):
        """Test state activities saving/loading
        """
        # all activities
        s1 = self.create(StateItem, uml2.State)
        s1.subject.name = 's1'
        s1.set_entry('test 1 entry')
        s1.set_exit('test 1 exit')
        s1.set_do_activity('test 1 do')

        # not all activities
        s2 = self.create(StateItem, uml2.State)
        s2.subject.name = 's2'
        s2.set_entry('test 2 entry')
        s2.set_do_activity('test 2 do')

        data = self.save()
        self.load(data)

        states = self.diagram.canvas.select(lambda e: isinstance(e, StateItem))
        self.assertEquals(2, len(states))
        s1, s2 = states
        if s1.subject.name == 's2':
            s1, s2 = s2, s1

        self.assertEquals('test 1 entry', s1.subject.entry.name)
        self.assertEquals('test 1 exit', s1.subject.exit.name)
        self.assertEquals('test 1 do', s1.subject.doActivity.name)
        self.assertEquals(3, len(s1._activities))
        self.assertTrue(s1._entry in s1._activities)
        self.assertTrue(s1._exit in s1._activities)
        self.assertTrue(s1._do_activity in s1._activities)

        self.assertEquals('test 2 entry', s2.subject.entry.name)
        self.assertTrue(s2.subject.exit is None)
        self.assertEquals('test 2 do', s2.subject.doActivity.name)
        self.assertEquals(2, len(s2._activities))
        self.assertTrue(s2._entry in s2._activities)
        self.assertFalse(s2._exit in s2._activities)
        self.assertTrue(s2._do_activity in s2._activities)

