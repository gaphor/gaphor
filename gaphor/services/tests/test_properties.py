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
from __future__ import absolute_import
from unittest import TestCase
from gaphor.services.properties import Properties, FileBackend
import tempfile

#class MockApplication(object):
#
#    def __init__(self):
#        self.events = []
#
#    def handle(self, event):
#        self.events.append(event)
#

class TestProperties(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        backend = FileBackend(self.tmpdir)
        self.properties = Properties(backend)
#        self.app = MockApplication()
        self.properties.init(self.app)

    def shutDown(self):
        self.properties.shutdown()
        os.remove(os.path.join(self.tmpdir, FileBackend.RESOURCE_FILE))
        os.rmdir(self.tmpdir)

#    def test_properties(self):
#        prop = self.properties
#        assert not self.app.events
#
#        prop.set('test1', 2)
#        assert len(self.app.events) == 1, self.app.events
#        event = self.app.events[0]
#        assert 'test1' == event.name
#        assert None is event.old_value
#        assert 2 is event.new_value
#        assert 2 == prop('test1')
#
#        prop.set('test1', 2)
#        assert len(self.app.events) == 1
#
#        prop.set('test1', 'foo')
#        assert len(self.app.events) == 2
#        event = self.app.events[1]
#        assert 'test1' == event.name
#        assert 2 is event.old_value
#        assert 'foo' is event.new_value
#        assert 'foo' == prop('test1')
#
#        assert 3 == prop('test2', 3)
#        assert 3 == prop('test2', 4)


# vim:sw=4:et:ai
