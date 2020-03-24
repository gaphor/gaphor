from gaphor import UML
from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.diagram.presentation import Classified
from gaphor.diagram.profiles.extension import ExtensionItem


@Connector.register(Classified, ExtensionItem)
class ExtensionConnect(RelationshipConnect):
    """Connect class and stereotype items using an extension item."""

    line: ExtensionItem

    def allow(self, handle, port):
        line = self.line
        subject = self.element.subject

        if handle is line.head:
            # Element at the head should be a class
            # (implies stereotype as well)
            allow = isinstance(subject, UML.Class)
        elif handle is line.tail:
            # Element at the tail should be a stereotype
            allow = isinstance(subject, UML.Stereotype)

        return allow and super().allow(handle, port)

    def connect_subject(self, handle):
        element = self.element
        line = self.line

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if c1 and c2:
            assert isinstance(c1.subject, UML.Class)
            assert isinstance(c2.subject, UML.Stereotype)

            head_type: UML.Class = c1.subject
            tail_type: UML.Stereotype = c2.subject

            # First check if we do not already contain the right subject:
            if line.subject:
                end1 = line.subject.memberEnd[0]
                end2 = line.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) or (
                    end2.type is head_type and end1.type is tail_type
                ):
                    return

            # TODO: make element at head end update!
            c1.request_update()

            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            ext: UML.Extension
            for ext in line.model.select(lambda e: isinstance(e, UML.Extension)):  # type: ignore[assignment]
                end1 = ext.memberEnd[0]
                end2 = ext.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) or (
                    end2.type is head_type and end1.type is tail_type
                ):
                    # check if this entry is not yet in the diagram
                    # Return if the association is not (yet) on the canvas
                    for item in ext.presentation:
                        if item.canvas is element.canvas:
                            break
                    else:
                        line.subject = ext
                        return
            else:
                # Create a new Extension relationship
                relation = UML.model.create_extension(head_type, tail_type)
                line.subject = relation

    def disconnect_subject(self, handle):
        """
        Disconnect model element.
        Disconnect property (memberEnd) too, in case of end of life for
        Extension.
        """
        opposite = self.line.opposite(handle)
        hct = self.get_connected(handle)
        oct = self.get_connected(opposite)
        if hct and oct:
            old = self.line.subject
            del self.line.subject
            if old and len(old.presentation) == 0:
                for e in old.memberEnd:
                    e.unlink()
                old.unlink()
