import pytest

from gaphor.C4Model.modelinglanguage import C4ModelLanguage


def test_modeling_language_name():
    ml = C4ModelLanguage()
    assert ml.name


@pytest.mark.parametrize(
    "name", ["C4Person", "C4SoftwareSystem", "C4Container", "C4Component"]
)
def test_elements(name):
    ml = C4ModelLanguage()

    assert ml.lookup_element(name)


@pytest.mark.parametrize(
    "name",
    [
        "C4PersonItem",
        "C4SoftwareSystemItem",
        "C4ContainerItem",
        "C4ContainerDatabaseItem",
        "C4ComponentItem",
    ],
)
def test_diagram_items(name):
    ml = C4ModelLanguage()

    assert ml.lookup_diagram_item(name)
