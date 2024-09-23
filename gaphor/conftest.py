"""Basic test case for Gaphor tests.

Everything is about services so the Case can define it's required
services and start off.
"""

# ruff: noqa: I001
from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

import gaphor.services.properties

# Load gaphor.ui first, so GTK library versions are set corrently
import gaphor.ui  # noqa: F401

from gaphas.view import GtkView

from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.core.modeling.modelinglanguage import (
    CoreModelingLanguage,
    MockModelingLanguage,
)
from gaphor.diagram.painter import ItemPainter
from gaphor.diagram.selection import Selection
from gaphor.storage import storage
from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.UML.modelinglanguage import UMLModelingLanguage
from gaphor.UML.sanitizerservice import SanitizerService


@pytest.fixture(autouse=True)
def assert_not_in_transaction():
    assert not Transaction.in_transaction()


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager, modeling_language):
    element_factory = ElementFactory(
        event_manager, ElementDispatcher(event_manager, modeling_language)
    )
    yield element_factory
    element_factory.shutdown()


@pytest.fixture
def modeling_language():
    return MockModelingLanguage(
        CoreModelingLanguage(), UMLModelingLanguage(), SysMLModelingLanguage()
    )


@pytest.fixture
def sanitizer_service(event_manager):
    sanitizer_service = SanitizerService(event_manager)
    yield sanitizer_service
    sanitizer_service.shutdown()


@pytest.fixture
def diagram(element_factory, event_manager):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)
    yield diagram
    with Transaction(event_manager):
        diagram.unlink()


@pytest.fixture
def create(diagram, element_factory):
    def _create(item_class, element_class=None):
        return diagram.create(
            item_class,
            subject=(element_factory.create(element_class) if element_class else None),
        )

    return _create


@pytest.fixture
def saver(element_factory):
    def save():
        """Save diagram into string."""

        f = StringIO()
        storage.save(f, element_factory)
        data = f.getvalue()
        f.close()

        return data

    return save


@pytest.fixture
def loader(element_factory, modeling_language):
    def load(data):
        """Load data from specified string."""
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(
            f, element_factory=element_factory, modeling_language=modeling_language
        )
        f.close()

    return load


@pytest.fixture
def test_models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "test-models"


@pytest.fixture
def models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "models"


@pytest.fixture
def view(diagram):
    view = GtkView(model=diagram, selection=Selection())
    item_painter = ItemPainter(view.selection)
    view.painter = item_painter
    view.bounding_box_painter = item_painter
    return view


@pytest.fixture(autouse=True)
def tmp_get_cache_config_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(gaphor.settings, "get_config_dir", lambda: tmp_path)
    monkeypatch.setattr(gaphor.settings, "get_cache_dir", lambda: tmp_path)
