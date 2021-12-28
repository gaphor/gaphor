import pytest

from gaphor.diagram.tests.fixtures import (
    diagram,
    element_factory,
    event_manager,
    modeling_language,
)
from gaphor.ui.styling import Styling


@pytest.fixture
def properties():
    return {}


@pytest.fixture(scope="session", autouse=True)
def styling():
    styling = Styling()
    yield styling
    styling.shutdown()
