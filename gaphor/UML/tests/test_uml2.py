# vim:sw=4:et:ai

import unittest

import gaphor.UML as UML

class TestUML2(unittest.TestCase):

    def test_element(self):
        a = UML.Element()
        b = UML.Element()
        def cb_func(name, *args):
            #print '  cb_func:', name, args
            pass

        a.connect('ev1', cb_func, a)
        a.connect('ev1', cb_func, a)
        a.connect('ev2', cb_func, 'ev2', a)

        print 'notify: ev1'
        a.notify('ev1')
        print 'notify: ev2'
        a.notify('ev2')

        a.disconnect(cb_func, a)

        print 'notify: ev1'
        a.notify('ev1')
        print 'notify: ev2'
        a.notify('ev2')

    def test1(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        c.package = p
        self.assertEquals(c.package, p)
        self.assertEquals(c.namespace, p)
        self.failUnless(c in p.ownedElement)
        
    def __on_owned_member(self, pspec, name):
        self.owned_member_called = True

    def testOwnedMember(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        self.owned_member_called = False
        p.connect('ownedMember', self.__on_owned_member)
        c.package = p
        self.assertEquals(self.owned_member_called, True)

    def testOwnedMember_Unlink(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        self.owned_member_called = False
        p.connect('ownedMember', self.__on_owned_member)
        c.package = p
        self.assertEquals(self.owned_member_called, True)
        self.owned_member_called = False
        c.unlink()
        self.assertEquals(self.owned_member_called, True)


if __name__ == '__main__':
    unittest.main()
