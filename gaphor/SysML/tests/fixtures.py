import pytest

from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.diagram.tests.fixtures import diagram, event_manager
from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


class MockModelingLanguage:
    def __init__(self):
        self._modeling_languages = [UMLModelingLanguage(), SysMLModelingLanguage()]

    def lookup_element(self, name):
        return self.first(lambda provider: provider.lookup_element(name))

    def first(self, predicate):
        for provider in self._modeling_languages:
            type = predicate(provider)
            if type:
                return type


@pytest.fixture
def element_factory(event_manager):  # noqa: F811
    return ElementFactory(
        event_manager, ElementDispatcher(event_manager, MockModelingLanguage())
    )
