"""Profile Import dependency relationship."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(
    UML.PackageImport,
    head=UML.PackageImport.importedPackage,
    tail=UML.PackageImport.importingNamespace,
)
class PackageImportItem(LinePresentation):
    """Profile Import dependency relationship."""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=text_stereotypes(
                self, lambda: [self.diagram.gettext("import")]
            ),
        )

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.watch("subject.appliedStereotype.classifier.name")
        self.draw_head = draw_arrow_head
