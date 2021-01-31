import pytest

from gaphor.core.modeling import StyleSheet
from gaphor.storage.parser import element
from gaphor.storage.storage import load_elements


@pytest.fixture
def loader(element_factory, modeling_language):
    def _loader(*parsed_elements):
        parsed_data = {p.id: p for p in parsed_elements}
        load_elements(parsed_data, element_factory, modeling_language)
        return element_factory.lselect()

    return _loader


def test_owned_comment_to_comment_upgrade(loader):
    c = element(id="1", type="Comment")
    c.references["annotatedElement"] = ["2"]
    e = element(id="2", type="Element")
    e.references["ownedComment"] = ["1"]

    comment, elem, style_sheet = loader(c, e)
    assert elem in comment.annotatedElement
    assert comment in elem.comment
    assert isinstance(style_sheet, StyleSheet)


def test_owned_classifier_to_owned_type(loader):
    p = element(id="1", type="Package")
    p.references["ownedClassifier"] = ["2"]
    c = element(id="2", type="Class")

    package, clazz, _ = loader(p, c)
    assert clazz in package.ownedType
    assert clazz.package is package
