import pytest

from gaphor import UML
from gaphor.plugins.xmiexport.exportmodel import XMIExport
from gaphor.UML.elementfactory import ElementFactory


@pytest.fixture
def element_factory():
    ef = ElementFactory()
    ef.create(UML.Package).name = "package"
    c1 = ef.create(UML.Class)
    c1.name = "class"
    c2 = ef.create(UML.Class)
    c2.name = "class"
    i1 = ef.create(UML.Interface)
    i1.name = "interface"
    c1.ownedAttribute = ef.create(UML.Property)
    c1.ownedAttribute[0].name = "attr"
    c1.ownedOperation = ef.create(UML.Operation)
    c1.ownedOperation[0].name = "oper"
    c1.ownedOperation[0].formalParameter = ef.create(UML.Parameter)

    UML.model.create_dependency(c1, c2)
    UML.model.create_generalization(c1, c2)
    UML.model.create_association(c1, c2)
    return ef


def test_xmi_export(element_factory, tmp_path):
    exporter = XMIExport(element_factory)
    f = tmp_path / "test.gaphor"

    exporter.export(f)

    content = f.read_text()

    assert '<XMI xmi.version="2.1"' in content
