"""Package Import connection adapters."""

from gaphor import UML
from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.diagram.presentation import Named
from gaphor.diagram.profiles.packageimport import PackageImportItem


@Connector.register(Named, PackageImportItem)
class PackageImportConnect(RelationshipConnect):
    """Connect an external model to a Package using an Import."""

    def allow(self, handle, port):
        line = self.line
        element = self.element

        # Element at the head should be a Package
        if handle is line.head and not isinstance(element.subject, UML.Package):
            return None

        # Element at the tail should also be a Package
        if handle is line.tail and not isinstance(element.subject, UML.Package):
            return None

        return super().allow(handle, port)

    def reconnect(self, handle, port):
        line = self.line
        impl = line.subject
        assert isinstance(impl, UML.Package)
        self.reconnect_relationship(
            handle,
            UML.PackageImport.importedPackage,
            UML.PackageImport.importingNamespace,
        )

    def connect_subject(self, handle):
        """Perform import package relationship connection."""
        relation = self.relationship_or_new(
            UML.PackageImport,
            UML.PackageImport.importedPackage,
            UML.PackageImport.importingNamespace,
        )
        self.line.subject = relation
