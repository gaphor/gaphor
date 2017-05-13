#!/usr/bin/env python

# Copyright (C) 2010-2017 Arjan Molenaar <gaphor@gmail.com>
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

import unittest

from gaphor.UML import uml2
from gaphor.application import Application


class PackageWithStereotypesRemovalTestCase(unittest.TestCase):
    def setUp(self):
        Application.init()
        element_factory = Application.get_service('element_factory')
        from gaphor.storage.storage import load
        load('tests/issue_53.gaphor', element_factory)

    def tearDown(self):
        Application.get_service('element_factory').shutdown()
        Application.shutdown()

    def testPackageRemoval(self):
        # Load the application
        element_factory = Application.get_service('element_factory')

        # Find all profile instances
        profiles = element_factory.lselect(lambda e: e.isKindOf(uml2.Profile))

        # Check there is 1 profile
        self.assertEquals(1, len(profiles))

        # Check the profile has 1 presentation
        self.assertEquals(1, len(profiles[0].presentation))

        # Unlink the presentation
        profiles[0].presentation[0].unlink()

        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(uml2.Profile)))

        classes = element_factory.lselect(lambda e: e.isKindOf(uml2.Class))
        self.assertEquals(1, len(classes))

        # Check if the link is really removed:
        self.assertFalse(classes[0].appliedStereotype)
        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(uml2.InstanceSpecification)))
        self.assertEquals(3, len(element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))))

    def testPackageRemovalByRemovingTheDiagram(self):
        element_factory = Application.get_service('element_factory')

        diagram = element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram) and e.name == 'Stereotypes diagram')[0]

        self.assertTrue(diagram)

        diagram.unlink()

        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(uml2.Profile)))

        classes = element_factory.lselect(lambda e: e.isKindOf(uml2.Class))
        self.assertEquals(1, len(classes))

        # Check if the link is really removed:
        self.assertFalse(classes[0].appliedStereotype)
        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(uml2.InstanceSpecification)))
        self.assertEquals(2, len(element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))))

# vim:sw=4:et:ai
