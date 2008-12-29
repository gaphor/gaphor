from gaphor.adapters.connectors import RelationshipConnect
from zope import interface, component
from gaphor import UML
from gaphor.diagram import items


class ExtensionConnect(RelationshipConnect):
    """
    Connect class and stereotype items using an extension item.
    """
    component.adapts(items.ClassifierItem, items.ExtensionItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element

        # Element at the head should be a Class
        if handle is line.head and \
           not isinstance(element.subject, UML.Class):
            return None

        # Element at the tail should be a Stereotype
        if handle is line.tail and \
           not isinstance(element.subject, UML.Stereotype):
            return None

        return super(ExtensionConnect, self).glue(handle, port)

    def connect_subject(self, handle):
        element = self.element
        line = self.line

        c1 = line.head.connected_to
        c2 = line.tail.connected_to
        if c1 and c2:
            head_type = c1.subject
            tail_type = c2.subject

            # First check if we do not already contain the right subject:
            if line.subject:
                end1 = line.subject.memberEnd[0]
                end2 = line.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    return
             
            # TODO: make element at head end update!
            c1.request_update()

            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            for assoc in self.element_factory.select():
                if isinstance(assoc, UML.Extension):
                    end1 = assoc.memberEnd[0]
                    end2 = assoc.memberEnd[1]
                    if (end1.type is head_type and end2.type is tail_type) \
                       or (end2.type is head_type and end1.type is tail_type):
                        # check if this entry is not yet in the diagram
                        # Return if the association is not (yet) on the canvas
                        for item in assoc.presentation:
                            if item.canvas is element.canvas:
                                break
                        else:
                            line.subject = assoc
                            return
            else:
                # Create a new Extension relationship
                relation = self.element_factory.create(UML.Extension)
                head_end = self.element_factory.create(UML.Property)
                tail_end = self.element_factory.create(UML.ExtensionEnd)
                relation.package = element.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                relation.ownedEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                tail_type.ownedAttribute = head_end
                head_end.name = 'baseClass'

                line.subject = relation

    def disconnect_subject(self, handle):
        """
        Disconnect model element.
        Disconnect property (memberEnd) too, in case of end of life for
        Extension
        """
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = self.line.subject
            del self.line.subject
            if old and len(old.presentation) == 0:
                for e in old.memberEnd:
                    e.unlink()
                old.unlink()


component.provideAdapter(ExtensionConnect)
