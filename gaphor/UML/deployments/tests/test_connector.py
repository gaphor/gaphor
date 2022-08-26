import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.core.modeling.modelinglanguage import (
    CoreModelingLanguage,
    MockModelingLanguage,
)
from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.UML.deployments.connector import ConnectorItem
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def modeling_language():
    return MockModelingLanguage(
        CoreModelingLanguage(), UMLModelingLanguage(), SysMLModelingLanguage()
    )


def test_create(create):
    """Test creation of connector item."""
    conn = create(ConnectorItem, UML.Connector)
    assert conn.subject is not None


def test_persistence(create, element_factory, saver, loader):
    """Test connector item saving/loading."""
    conn = create(ConnectorItem, UML.Connector)

    end = element_factory.create(UML.ConnectorEnd)
    conn.subject.end = end

    data = saver()
    assert end.id in data

    loader(data)
    diagram = next(element_factory.select(Diagram))
    assert diagram.select(ConnectorItem)
    assert element_factory.lselect(UML.ConnectorEnd)
