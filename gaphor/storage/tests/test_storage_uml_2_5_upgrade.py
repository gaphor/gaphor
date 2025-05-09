import pytest

from gaphor.core.modeling import StyleSheet
from gaphor.storage.load import load_elements
from gaphor.storage.parser import element


@pytest.fixture
def loader(element_factory, modeling_language):
    def _loader(*parsed_elements):
        parsed_data = {p.id: p for p in parsed_elements}
        load_elements(parsed_data, element_factory, modeling_language)
        *elements, style_sheet = element_factory.lselect()
        assert isinstance(style_sheet, StyleSheet)
        return elements

    return _loader


def test_owned_comment_to_comment_upgrade(loader):
    c = element(id="1", type="Comment")
    c.references["annotatedElement"] = ["2"]
    e = element(id="2", type="Element")
    e.references["ownedComment"] = ["1"]

    comment, elem = loader(c, e)
    assert elem in comment.annotatedElement
    assert comment in elem.comment


def test_owned_classifier_to_owned_type(loader):
    p = element(id="1", type="Package")
    p.references["ownedClassifier"] = ["2"]
    c = element(id="2", type="Class")

    package, clazz = loader(p, c)
    assert clazz in package.ownedType
    assert clazz.package is package


def test_implementation_to_interface_realization(loader):
    i = element(id="1", type="InterfaceRealization")
    c = element(id="2", type="Class")
    c.references["interfaceRealization"] = ["1"]

    interface_realization, clazz = loader(i, c)
    assert interface_realization in clazz.clientDependency
    assert clazz is interface_realization.implementingClassifier


def test_formal_parameter_to_owned_parameter(loader):
    o = element(id="1", type="Operation")
    o.references["formalParameter"] = ["2"]
    p = element(id="2", type="Parameter")

    operation, parameter = loader(o, p)
    assert parameter in operation.ownedParameter
    assert parameter.operation is operation


def test_return_result_to_owned_parameter(loader):
    o = element(id="1", type="Operation")
    o.references["returnResult"] = ["2"]
    p = element(id="2", type="Parameter")
    p.references["ownerReturnParam"] = ["1"]

    operation, parameter = loader(o, p)
    assert parameter in operation.ownedParameter
    assert parameter.operation is operation


def test_parameters_to_owned_parameter(loader):
    o = element(id="1", type="Operation")
    o.references["formalParameter"] = ["2"]
    o.references["returnResult"] = ["3"]
    p = element(id="2", type="Parameter")
    r = element(id="3", type="Parameter")

    operation, parameter, return_param = loader(o, p, r)
    assert parameter in operation.ownedParameter
    assert return_param in operation.ownedParameter
    assert parameter.operation is operation
    assert return_param.operation is operation
