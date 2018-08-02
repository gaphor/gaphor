
import os
import unittest

import pkg_resources

from gaphor import UML
from gaphor.application import Application


class PackageWithStereotypesRemovalTestCase(unittest.TestCase):

    def setUp(self):
        Application.init()
        element_factory = Application.get_service('element_factory')
        from gaphor.storage.storage import load

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'tests/issue_53.gaphor')
        load(path, element_factory)

    def tearDown(self):
        Application.get_service('element_factory').shutdown()
        Application.shutdown()

    def testPackageRemoval(self):
        # Load the application
        element_factory = Application.get_service('element_factory')

        # Find all profile instances
        profiles = element_factory.lselect(lambda e: e.isKindOf(UML.Profile))
        
        # Check there is 1 profile
        self.assertEquals(1, len(profiles))

        # Check the profile has 1 presentation
        self.assertEquals(1, len(profiles[0].presentation))

        # Unlink the presentation
        profiles[0].presentation[0].unlink()

        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(UML.Profile)))

        classes = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
        self.assertEquals(1, len(classes))

        # Check if the link is really removed:
        self.assertFalse(classes[0].appliedStereotype)
        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(UML.InstanceSpecification)))
        self.assertEquals(3, len(element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))))

    def testPackageRemovalByRemovingTheDiagram(self):
        element_factory = Application.get_service('element_factory')

        diagram = element_factory.lselect(lambda e: e.isKindOf(UML.Diagram) and e.name == 'Stereotypes diagram')[0]
        
        self.assertTrue(diagram)

        diagram.unlink()

        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(UML.Profile)))

        classes = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
        self.assertEquals(1, len(classes))

        # Check if the link is really removed:
        self.assertFalse(classes[0].appliedStereotype)
        self.assertFalse(element_factory.lselect(lambda e: e.isKindOf(UML.InstanceSpecification)))
        self.assertEquals(2, len(element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))))

# vim:sw=4:et:ai
