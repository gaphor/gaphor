import pytest

from gaphor.conftest import Case


@pytest.fixture
def case():
    case = Case()
    yield case
    case.shutdown()
