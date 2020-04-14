from io import StringIO

import pytest

from gaphor.diagram.tests.fixtures import diagram, element_factory, event_manager
from gaphor.storage import storage
from gaphor.UML.modelprovider import UMLModelProvider


@pytest.fixture
def model_provider():
    return UMLModelProvider()


@pytest.fixture
def loader(element_factory, model_provider):
    def load(data):
        """
        Load data from specified string.
        """
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(f, factory=element_factory, model_provider=model_provider)
        f.close()

    return load
