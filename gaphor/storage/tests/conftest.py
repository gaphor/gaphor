from io import StringIO

import pytest

from gaphor.diagram.tests.fixtures import diagram, element_factory, event_manager
from gaphor.storage import storage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def modeling_language():
    return UMLModelingLanguage()


@pytest.fixture
def loader(element_factory, modeling_language):  # noqa: F811
    def load(data):
        """
        Load data from specified string.
        """
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(f, factory=element_factory, modeling_language=modeling_language)
        f.close()

    return load
