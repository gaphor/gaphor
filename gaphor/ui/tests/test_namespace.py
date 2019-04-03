from gaphor.tests.testcase import TestCase
import gaphor.UML as UML
from gaphor.ui.namespace import NamespaceModel
from gaphor.application import Application


class NamespaceTestCase(TestCase):

    services = ["element_factory"]

    def tearDown(self):
        pass

    def test(self):
        factory = Application.get_service("element_factory")

        ns = NamespaceModel(factory)

        m = factory.create(UML.Package)
        m.name = "m"
        assert m in ns._nodes
        assert ns.path_from_element(m) == (1,)
        assert ns.element_from_path((1,)) is m

        a = factory.create(UML.Package)
        a.name = "a"
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

        c = factory.create(UML.Class)
        c.name = "c"
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



