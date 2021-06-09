import pytest

from gaphor.C4Model.modelinglanguage import C4ModelLanguage


def test_modeling_language_name():
    ml = C4ModelLanguage()
    assert ml.name


@pytest.mark.parametrize("name", ["C4Person", "C4Container"])
def test_elements(name):
    ml = C4ModelLanguage()

    assert ml.lookup_element(name)


@pytest.mark.parametrize(
    "name",
    [
        "C4PersonItem",
        "C4ContainerItem",
        "C4DatabaseItem",
    ],
)
def test_diagram_items(name):
    ml = C4ModelLanguage()

    assert ml.lookup_element(name)
