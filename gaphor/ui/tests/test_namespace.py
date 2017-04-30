# vim:sw=4:et:ai

from __future__ import absolute_import
from __future__ import print_function

from gaphor.UML import uml2
from gaphor.application import Application
from gaphor.tests.testcase import TestCase
from gaphor.ui.namespace import NamespaceModel


class NamespaceTestCase(object):  ##TestCase):

    services = ['element_factory']

    def test_all(self):
        factory = Application.get_service('element_factory')

        m = factory.create(uml2.Package)
        m.name = 'm'
        a = factory.create(uml2.Package)
        a.name = 'a'
        a.package = m
        assert a.package is m
        assert a in m.ownedMember
        assert a.namespace is m

        b = factory.create(uml2.Package)
        b.name = 'b'
        b.package = a
        assert b in a.ownedMember
        assert b.namespace is a

        c = factory.create(uml2.Class)
        c.name = 'c'
        c.package = b
        d = factory.create(uml2.Class)
        d.name = 'd'
        d.package = a
        e = factory.create(uml2.Class)
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

        print('---')
        print(ns.root)
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 0, 0), ns.path_from_element(b)
        assert ns.path_from_element(c) == (0, 0, 0, 0)
        assert ns.path_from_element(d) == (0, 0, 1)
        assert ns.path_from_element(e) == (0, 0, 0, 1)

        return

        print('--- del.b.ownedClassifier[c]')
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
            pass  # Yes, should raise an exception
        else:
            assert ns.path_from_element(c) is not None

        print('--- c.package = a')
        c.package = a
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 0, 0)
        assert ns.path_from_element(c) == (0, 0, 1)
        assert ns.path_from_element(d) == (0, 0, 2)
        assert ns.path_from_element(e) == (0, 0, 0, 0)

        print('--- b.package = m')
        b.package = m
        ns.dump()
        assert ns.path_from_element(m) == (0,)
        assert ns.path_from_element(a) == (0, 0)
        assert ns.path_from_element(b) == (0, 1)
        assert ns.path_from_element(c) == (0, 0, 0)
        assert ns.path_from_element(d) == (0, 0, 1)
        assert ns.path_from_element(e) == (0, 1, 0)

        print('--- e.unlink()')
        e.unlink()
        ns.dump()

        print('--- a.unlink()')
        #        def on_unlink(name, element):
        #            print 'unlink: %s' % element.name
        #        a.connect('__unlink__', on_unlink, a)
        #        b.connect('__unlink__', on_unlink, b)
        #        c.connect('__unlink__', on_unlink, c)
        #        d.connect('__unlink__', on_unlink, d)
        #
        a.unlink()
        ns.dump()
        print('--- TODO: e.relink()')

        print(uml2.Class.package)
        print(uml2.Package.ownedClassifier)


class NewNamespaceTestCase(TestCase):
    services = ['element_factory']

    def tearDown(self):
        pass

    def test(self):
        factory = Application.get_service('element_factory')

        ns = NamespaceModel(factory)

        m = factory.create(uml2.Package)
        m.name = 'm'
        assert m in ns._nodes
        assert ns.path_from_element(m) == (1,)
        assert ns.element_from_path((1,)) is m

        a = factory.create(uml2.Package)
        a.name = 'a'
        assert a in ns._nodes
        assert a in ns._nodes[None]
        assert m in ns._nodes
        assert ns.path_from_element(a) == (1,), ns.path_from_element(a)
        assert ns.path_from_element(m) == (2,), ns.path_from_element(m)

        a.package = m
        assert a in ns._nodes
        assert a not in ns._nodes[None]
        assert a in ns._nodes[m]
        assert m in ns._nodes
        assert a.package is m
        assert a in m.ownedMember
        assert a.namespace is m
        assert ns.path_from_element(a) == (1, 0), ns.path_from_element(a)

        c = factory.create(uml2.Class)
        c.name = 'c'
        assert c in ns._nodes
        assert ns.path_from_element(c) == (1,), ns.path_from_element(c)
        assert ns.path_from_element(m) == (2,), ns.path_from_element(m)
        assert ns.path_from_element(a) == (2, 0), ns.path_from_element(a)

        c.package = m
        assert c in ns._nodes
        assert c not in ns._nodes[None]
        assert c in ns._nodes[m]

        c.package = a
        assert c in ns._nodes
        assert c not in ns._nodes[None]
        assert c not in ns._nodes[m]
        assert c in ns._nodes[a]

        c.unlink()
        assert c not in ns._nodes
        assert c not in ns._nodes[None]
        assert c not in ns._nodes[m]
        assert c not in ns._nodes[a]


if __name__ == '__main__':
    import unittest

    unittest.main()
