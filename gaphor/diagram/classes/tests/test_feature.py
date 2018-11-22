
from gaphor.tests.testcase import TestCase
from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.compartment import FeatureItem
from gaphor.UML.diagram import DiagramCanvas


class FeatureTestCase(TestCase):

    def setUp(self):
        super(FeatureTestCase, self).setUp()

    def tearDown(self):
        super(FeatureTestCase, self).tearDown()

    def testAttribute(self):
        """
        Test how attribute is updated
        """
        attr = self.element_factory.create(UML.Property)
        UML.parse(attr, '-name:myType')

        clazzitem = self.create(ClassItem, UML.Class)
        clazzitem.subject.ownedAttribute = attr
        self.assertEqual(1, len(clazzitem._compartments[0]))

        item = clazzitem._compartments[0][0]
        self.assertTrue(isinstance(item, FeatureItem))

        size = item.get_size()
        self.assertNotEquals((0, 0), size)

        attr.defaultValue = 'myDefault'

        self.diagram.canvas.update()
        self.assertTrue(size < item.get_size())



# vim:sw=4:et:ai
