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

