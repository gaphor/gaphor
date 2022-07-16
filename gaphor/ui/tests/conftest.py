import pytest

from gaphor.ui.styling import Styling


class MockProperties(dict):
    def set(self, key, value):
        self[key] = value


@pytest.fixture
def properties():
    return MockProperties()


@pytest.fixture(scope="session", autouse=True)
def styling():
    styling = Styling()
    yield styling
    styling.shutdown()
