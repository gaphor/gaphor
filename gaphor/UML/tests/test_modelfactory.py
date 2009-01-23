from gaphor import UML
from gaphor.application import Application


import unittest

class StereotypesTest(unittest.TestCase):
    def setUp(self):
        Application.init_components()
        self.factory = UML.ElementFactory()
        self.factory.init(Application)

    def test_stereotype_name(self):
        """Test stereotype name
        """
        stereotype = self.factory.create(UML.Stereotype)
        stereotype.name = 'Test'
        self.assertEquals('test', UML.model.stereotype_name(stereotype))

        stereotype.name = 'TEST'
        self.assertEquals('TEST', UML.model.stereotype_name(stereotype))

        stereotype.name = 'T'
        self.assertEquals('t', UML.model.stereotype_name(stereotype))


    def test_stereotypes_conversion(self):
        """Test stereotypes conversion
        """
        s1 = self.factory.create(UML.Stereotype)
        s2 = self.factory.create(UML.Stereotype)
        s3 = self.factory.create(UML.Stereotype)
        s1.name = 's1'
        s2.name = 's2'
        s3.name = 's3'

        cls = self.factory.create(UML.Class)
        cls.appliedStereotype = s1
        cls.appliedStereotype = s2
        cls.appliedStereotype = s3

        self.assertEquals('s1, s2, s3', UML.model.stereotypes_str(cls))


    def test_no_stereotypes(self):
        """Test stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(UML.Class)
        self.assertEquals('', UML.model.stereotypes_str(cls))


    def test_additional_stereotypes(self):
        """Test additional stereotypes conversion
        """
        s1 = self.factory.create(UML.Stereotype)
        s2 = self.factory.create(UML.Stereotype)
        s3 = self.factory.create(UML.Stereotype)
        s1.name = 's1'
        s2.name = 's2'
        s3.name = 's3'

        cls = self.factory.create(UML.Class)
        cls.appliedStereotype = s1
        cls.appliedStereotype = s2
        cls.appliedStereotype = s3

        result = UML.model.stereotypes_str(cls, ('test',))
        self.assertEquals('test, s1, s2, s3', result)


    def test_just_additional_stereotypes(self):
        """Test additional stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(UML.Class)

        result = UML.model.stereotypes_str(cls, ('test',))
        self.assertEquals('test', result)



# vim:sw=4:et
