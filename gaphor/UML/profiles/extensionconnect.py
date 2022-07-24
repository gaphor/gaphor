from gaphor import UML
from gaphor.diagram.connectors import Connector, DirectionalRelationshipConnect
from gaphor.diagram.presentation import Classified
from gaphor.UML.profiles.extension import ExtensionItem
from gaphor.UML.recipes import owner_package


@Connector.register(Classified, ExtensionItem)
class ExtensionConnect(DirectionalRelationshipConnect):
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
        assert element.diagram

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
            for ext in line.model.select(UML.Extension):
                end1 = ext.memberEnd[0]
                end2 = ext.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) or (
                    end2.type is head_type and end1.type is tail_type
                ):
                    # check if this entry is not yet in the diagram
                    # Return if the association is not (yet) on the diagram
                    for item in ext.presentation:
                        if item.diagram is element.diagram:
                            break
                    else:
                        line.subject = ext
                        return
            # Create a new Extension relationship
            relation = UML.recipes.create_extension(head_type, tail_type)
            relation.package = owner_package(element.diagram.owner)
            line.subject = relation

    def disconnect_subject(self, handle) -> None:
        extension = self.line.subject
        if extension:
            UML.recipes.unapply_stereotype_by_extension(extension)
        return super().disconnect_subject(handle)
