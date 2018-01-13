#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test the backup service.
"""

from __future__ import absolute_import
from StringIO import StringIO
from gaphor.storage import storage
from gaphor.application import Application
from gaphor.misc.xmlwriter import XMLWriter
from six.moves import map

#class BackupServiceTestCase(unittest.TestCase):
class BackupServiceTestCase:

    services = ['element_factory', 'backup_service']

    def setUp(self):
        Application.init(services=self.services)
        self.element_factory = Application.get_service('element_factory')
        self.backup_service = Application.get_service('backup_service')

    def tearDown(self):
        Application.shutdown()
        
    def save_and_load(self, filename):
        factory = self.element_factory

        f = open(filename, 'r')
        storage.load(f, factory=self.element_factory)
        f.close()
        
        self.backup_service.backup()
        
        elements = list(map(factory.lookup, list(factory.keys())))

        orig = StringIO()
        storage.save(XMLWriter(orig), factory=self.element_factory)

        self.backup_service.restore()

        restored = list(map(factory.lookup, list(factory.keys())))

        assert len(elements) == len(restored)
        assert elements != restored

        copy = StringIO()
        storage.save(XMLWriter(copy), factory=self.element_factory)

        orig = orig.getvalue()
        copy = copy.getvalue()
        assert len(orig) == len(copy)
        #assert orig == copy, orig + ' != ' + copy


    def test_simple(self):
        self.save_and_load('test-diagrams/simple-items.gaphor')


    def test_namespace(self):
        self.save_and_load('test-diagrams/namespace.gaphor')

    def test_association(self):
        self.save_and_load('test-diagrams/association.gaphor')

    def test_interactions(self):
        self.save_and_load('test-diagrams/interactions.gaphor')

    def test_bicycle(self):
        self.save_and_load('test-diagrams/bicycle.gaphor')

    def test_line_align(self):
        self.save_and_load('test-diagrams/line-align.gaphor')

#    def test_gaphas_canvas(self):
#        self.save_and_load('../gaphas/gaphor-canvas.gaphor')

    def test_stereotype(self):
        self.save_and_load('test-diagrams/stereotype.gaphor')


# vim: sw=4:et:ai
