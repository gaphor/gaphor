
from gaphor.tests.testcase import TestCase
from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.classes.feature import AttributeItem, OperationItem
from gaphor.diagram.compartment import SlotItem
from gaphor.UML.diagram import DiagramCanvas


class FeatureTestCase(TestCase):

    def setUp(self):
        super(FeatureTestCase, self).setUp()

    def tearDown(self):
        super(FeatureTestCase, self).tearDown()

    def testAttribute(self):
        """
        Test how attribute is updated.
        """
        attr = self.element_factory.create(UML.Property)
        attr.parse('-name:myType')

        self.assertEquals('- name: myType', attr.render())

        clazzitem = self.create(ClassItem, UML.Class)

        clazzitem.subject.ownedAttribute = attr
        assert len(clazzitem._compartments[0]) == 1

        item = clazzitem._compartments[0][0]
        assert isinstance(item, AttributeItem)

        assert item.get_size() != (0, 0), item.get_size()
        size = item.get_size()

        attr.defaultValue = self.element_factory.create(UML.LiteralSpecification)
        attr.defaultValue.value = 'myDefault'

        self.assertEquals('- name: myType = myDefault', attr.render())
        
        self.diagram.canvas.update()
        #assert size != item.get_size(), item.get_size()



# vim:sw=4:et:ai
