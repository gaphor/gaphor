import pytest

from gaphor.diagram.tests.fixtures import diagram, element_factory, event_manager


@pytest.fixture
def create(diagram, element_factory):
    def _create(item_class, element_class=None):
        return diagram.create(
            item_class,
            subject=(element_factory.create(element_class) if element_class else None),
        )

    return _create
