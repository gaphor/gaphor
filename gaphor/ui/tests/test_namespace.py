# vim:sw=4:et:ai

from gaphor.tests.testcase import TestCase
import gaphor.UML as UML
from gaphor.ui.namespace import NamespaceModel, NewNamespaceModel
from gaphor.application import Application

class NamespaceTestCase(object): ##TestCase):

    services = [ 'element_factory' ]

    def test_all(self):
        factory = Application.get_service('element_factory')

        m = factory.create(UML.Package)
        m.name = 'm'
        a = factory.create(UML.Package)
        a.name = 'a'
        a.package = m
        assert a.package is m
        assert a in m.ownedMember
        assert a.namespace is m

        b = factory.create(UML.Package)
        b.name = 'b'
        b.package = a
        assert b in a.ownedMember
        assert b.namespace is a

        c = factory.create(UML.Class)
        c.name = 'c'
        c.package = b
        d = factory.create(UML.Class)
        d.name = 'd'
        d.package = a
        e = factory.create(UML.Class)
        e.name = 'e'
        e.package = b

        assert c in b.ownedMember
        assert c.namespace is b
        assert d in a.ownedMember
        assert d.namespace is a
        assert e in b.ownedMember
        assert e.namespace is b

        ns = NamespaceModel(factory)

        # We have a model loaded. Use it!
        factory.notify_model()

        print '---'
        print ns.root
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 0, 0), ns.path_from_element(b)
        assert ns.path_from_element(c) == (0, 0, 0, 0)
        assert ns.path_from_element(d) == (0, 0, 1)
        assert ns.path_from_element(e) == (0, 0, 0, 1)

        return


        print '--- del.b.ownedClassifier[c]'
        del b.ownedClassifier[c]
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 0, 0)
        assert ns.path_from_element(d) == (0, 0, 1)
        assert ns.path_from_element(e) == (0, 0, 0, 0), ns.path_from_element(e)
        try:
            ns.path_from_element(c)
        except AttributeError:
            pass # Yes, should raise an exception
        else:
            assert ns.path_from_element(c) is not None

        print '--- c.package = a'
        c.package = a
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 0, 0)
        assert ns.path_from_element(c) == (0, 0, 1)
        assert ns.path_from_element(d) == (0, 0, 2)
        assert ns.path_from_element(e) == (0, 0, 0, 0)

        print '--- b.package = m'
        b.package = m
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 1)
        assert ns.path_from_element(c) == (0, 0, 0)
        assert ns.path_from_element(d) == (0, 0, 1)
        assert ns.path_from_element(e) == (0, 1, 0)

        print '--- e.unlink()'
        e.unlink()
        ns.dump()

        print '--- a.unlink()'
#        def on_unlink(name, element):
#            print 'unlink: %s' % element.name
#        a.connect('__unlink__', on_unlink, a)
#        b.connect('__unlink__', on_unlink, b)
#        c.connect('__unlink__', on_unlink, c)
#        d.connect('__unlink__', on_unlink, d)
#
        a.unlink()
        ns.dump()
        print '--- TODO: e.relink()'

        print UML.Class.package
        print UML.Package.ownedClassifier


class NewNamespaceTestCase(TestCase):

    services = [ 'element_factory' ]

    def test(self):
        factory = Application.get_service('element_factory')

        ns = NewNamespaceModel(factory)

        m = factory.create(UML.Package)
        m.name = 'm'
        assert ns._nodes.has_key(m)
        assert ns.path_from_element(m) == (0,)
        assert ns.element_from_path((0,)) is m

        a = factory.create(UML.Package)
        a.name = 'a'
        assert a in ns._nodes
        assert m in ns._nodes
        assert ns.path_from_element(a) == (1,) 

        a.package = m
        assert a in ns._nodes
        assert a in ns._nodes[m]
        assert m in ns._nodes
        assert a.package is m
        assert a in m.ownedMember
        assert a.namespace is m
        assert ns.path_from_element(a) == (0, 0), ns.path_from_element(a)

if __name__ == '__main__':
    import unittest
    unittest.main()
