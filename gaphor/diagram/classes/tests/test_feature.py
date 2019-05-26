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
        UML.parse(attr, "-name:myType")

        clazzitem = self.create(ClassItem, UML.Class)
        clazzitem.subject.ownedAttribute = attr
        assert 1 == len(clazzitem._compartments[0])

        item = clazzitem._compartments[0][0]
        assert isinstance(item, FeatureItem)

        size = item.get_size()
        assert (0, 0) != size

        attr.defaultValue = "myDefault"

        self.diagram.canvas.update()
        assert size < item.get_size()
