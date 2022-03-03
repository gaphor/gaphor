"""Basic test case for Gaphor tests.

Everything is about services so the Case can define it's required
services and start off.
"""
from __future__ import annotations

# isort: skip_file

import logging
from io import StringIO
from pathlib import Path
from typing import TypeVar

import pytest

# Load gaphor.ui first, so GTK library versions are set corrently
import gaphor.ui

from gaphas.connector import ConnectionSink
from gaphas.connector import Connector as ConnectorAspect
from gaphas.painter import BoundingBoxPainter
from gaphas.view import GtkView

# For DiagramItemConnector aspect:
import gaphor.diagram.tools
from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.application import Session
from gaphor.diagram.connectors import Connector
from gaphor.diagram.painter import ItemPainter
from gaphor.diagram.selection import Selection


T = TypeVar("T")
S = TypeVar("S")

log = logging.getLogger("Gaphor")
log.setLevel(logging.WARNING)


class Case:
    services = [
        "event_manager",
        "component_registry",
        "element_factory",
        "element_dispatcher",
        "modeling_language",
        "sanitizer",
    ]

    def __init__(self):
        self.session = Session(services=self.services)
        self.element_factory = self.session.get_service("element_factory")
        self.modeling_language = self.session.get_service("modeling_language")
        assert not list(self.element_factory.select()), list(
            self.element_factory.select()
        )
        self.diagram = self.element_factory.create(Diagram)

        # We need to hook up a view for now, so updates are done instantly
        self.view = GtkView(self.diagram, selection=Selection())
        self.view.painter = ItemPainter(self.view.selection)
        self.view.bounding_box_painter = BoundingBoxPainter(self.view.painter)
        assert len(list(self.element_factory.select())) == 1, list(
            self.element_factory.select()
        )

    def get_service(self, name):
        return self.session.get_service(name)

    def create(
        self,
        item_cls: type[T],
        subject_cls: type[S] | None = None,
        subject: S | None = None,
    ) -> T:
        """Create an item with specified subject."""
        if subject_cls is not None:
            subject = self.element_factory.create(subject_cls)
        item: T = self.diagram.create(item_cls, subject=subject)
        self.diagram.update_now((item,))
        return item

    def allow(self, line, handle, item, port=None):
        """Glue line's handle to an item.

        If port is not provided, then first port is used.
        """
        if port is None and len(item.ports()) > 0:
            port = item.ports()[0]

        adapter = Connector(item, line)
        return adapter.allow(handle, port)

    def connect(self, line, handle, item):
        """Connect line's handle to an item."""
        diagram = line.diagram
        assert diagram is item.diagram

        sink = ConnectionSink(item, distance=1e4)
        connector = ConnectorAspect(line, handle, diagram.connections)

        connector.connect(sink)

        cinfo = diagram.connections.get_connection(handle)
        assert cinfo.connected is item
        assert cinfo.port

    def disconnect(self, line, handle):
        """Disconnect line's handle."""
        diagram = self.diagram
        # disconnection on adapter level is performed due to callback, so
        # no adapter look up here
        diagram.connections.disconnect_item(line, handle)
        assert not diagram.connections.get_connection(handle)

    def get_connected(self, handle):
        """Get item connected to line via handle."""
        if cinfo := self.diagram.connections.get_connection(handle):
            return cinfo.connected
        return None

    def get_connection(self, handle):
        """Get connection information."""
        return self.diagram.connections.get_connection(handle)

    def kindof(self, cls):
        """Find UML metaclass instances using element factory."""
        return self.element_factory.lselect(cls)

    def save(self):
        """Save diagram into string."""
        from gaphor.storage import storage
        from gaphor.storage.xmlwriter import XMLWriter

        f = StringIO()
        storage.save(XMLWriter(f), factory=self.element_factory)
        data = f.getvalue()
        f.close()

        self.element_factory.flush()
        assert not list(self.element_factory.select())
        assert not list(self.element_factory.lselect())
        return data

    def load(self, data):
        """Load data from specified string.

        Update ``Case.diagram`` attribute to hold new loaded diagram.
        """
        from gaphor.storage import storage

        f = StringIO(data)
        storage.load(
            f, factory=self.element_factory, modeling_language=self.modeling_language
        )
        f.close()

        self.diagram = self.element_factory.lselect(Diagram)[0]

    def shutdown(self):
        self.element_factory.shutdown()
        self.session.shutdown()


@pytest.fixture
def case():
    case = Case()
    yield case
    case.shutdown()


@pytest.fixture
def test_models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "test-models"


@pytest.fixture
def models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "models"
