import pytest

from gaphor.C4Model.modelinglanguage import C4ModelLanguage
from gaphor.core.modeling.modelinglanguage import CoreModelingLanguage
from gaphor.diagram.tests.fixtures import (
    MockModelingLanguage,
    diagram,
    element_factory,
    event_manager,
)
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def modeling_language():
    return MockModelingLanguage(
        CoreModelingLanguage(), UMLModelingLanguage(), C4ModelLanguage()
    )
