import pytest

from gaphor.core.modeling.modelinglanguage import CoreModelingLanguage
from gaphor.diagram.tests.fixtures import MockModelingLanguage
from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def modeling_language():
    return MockModelingLanguage(
        CoreModelingLanguage(), UMLModelingLanguage(), SysMLModelingLanguage()
    )
