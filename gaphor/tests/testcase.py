"""Basic test case for Gaphor tests.

Everything is about services so the TestCase can define it's required
services and start off.
"""

import logging
import unittest
from io import StringIO
from typing import Type, TypeVar

from gaphas.aspect.connector import ConnectionSink
from gaphas.aspect.connector import Connector as ConnectorAspect
from gaphas.painter import BoundingBoxPainter
from gaphas.view import GtkView

# For DiagramItemConnector aspect:
import gaphor.diagram.diagramtools  # noqa
from gaphor import UML
from gaphor.application import Session
from gaphor.diagram.connectors import Connector
from gaphor.diagram.grouping import Group
from gaphor.diagram.painter import ItemPainter
from gaphor.diagram.selection import Selection

T = TypeVar("T")

log = logging.getLogger("Gaphor")
log.setLevel(logging.WARNING)


class TestCase(unittest.TestCase):

    services = [
        "event_manager",
        "component_registry",
        "element_factory",
        "element_dispatcher",
        "modeling_language",
        "sanitizer",
    ]

    def setUp(self):
        self.session = Session(services=self.services)
        self.element_factory = self.session.get_service("element_factory")
        self.modeling_language = self.session.get_service("modeling_language")
        assert len(list(self.element_factory.select())) == 0, list(
            self.element_factory.select()
        )
        self.diagram = self.element_factory.create(UML.Diagram)

        # We need to hook up a view for now, so updates are done instantly
        self.view = GtkView(self.diagram, selection=Selection())
        self.view.painter = ItemPainter(self.view.selection)
        self.view.bounding_box_painter = BoundingBoxPainter(self.view.painter)
        assert len(list(self.element_factory.select())) == 1, list(
            self.element_factory.select()
        )

    def tearDown(self):
        self.element_factory.shutdown()
        self.session.shutdown()

    def get_service(self, name):
        return self.session.get_service(name)

    def create(self, item_cls: Type[T], subject_cls=None, subject=None) -> T:
        """Create an item with specified subject."""
        if subject_cls is not None:
            subject = self.element_factory.create(subject_cls)
        item = self.diagram.create(item_cls, subject=subject)
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
        cinfo = self.diagram.connections.get_connection(handle)
        if cinfo:
            return cinfo.connected
        return None

    def get_connection(self, handle):
        """Get connection information."""
        return self.diagram.connections.get_connection(handle)

    def can_group(self, parent, item):
        """Check if an item can be grouped by parent."""
        adapter = Group(parent, item)
        return adapter.can_contain()

    def group(self, parent, item):
        """Group item within a parent."""
        item.parent = parent
        adapter = Group(parent, item)
        adapter.group()

    def ungroup(self, parent, item):
        """Remove item from a parent."""
        adapter = Group(parent, item)
        adapter.ungroup()
        item.parent = None

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

        Update ``TestCase.diagram`` attribute to hold new loaded
        diagram.
        """
        from gaphor.storage import storage

        f = StringIO(data)
        storage.load(
            f, factory=self.element_factory, modeling_language=self.modeling_language
        )
        f.close()

        self.diagram = self.element_factory.lselect(UML.Diagram)[0]
