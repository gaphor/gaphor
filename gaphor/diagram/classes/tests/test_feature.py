
from __future__ import absolute_import
from gaphor.tests.testcase import TestCase
from gaphor.UML import uml2
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.compartment import FeatureItem


class FeatureTestCase(TestCase):

    def setUp(self):
        super(FeatureTestCase, self).setUp()

    def tearDown(self):
        super(FeatureTestCase, self).tearDown()

    def testAttribute(self):
        """
        Test how attribute is updated
        """
        attr = self.element_factory.create(uml2.Property)
        parse(attr, '-name:myType')

        clazzitem = self.create(ClassItem, uml2.Class)
        clazzitem.subject.ownedAttribute = attr
        self.assertEquals(1, len(clazzitem._compartments[0]))

        item = clazzitem._compartments[0][0]
        self.assertTrue(isinstance(item, FeatureItem))

        size = item.get_size()
        self.assertNotEquals((0, 0), size)

        attr.defaultValue = 'myDefault'

        self.diagram.canvas.update()
        self.assertTrue(size < item.get_size())



# vim:sw=4:et:ai
