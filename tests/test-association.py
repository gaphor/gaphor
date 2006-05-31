
import gaphor
import gaphor.UML as UML
import gaphor.diagram as diagram

factory = gaphor.resource(UML.ElementFactory)

d = factory.create(UML.Diagram)
c1 = factory.create(UML.Class)
c2 = factory.create(UML.Class)

ci1 = d.create(diagram.ClassItem)
ci1.subject = c1
ci2 = d.create(diagram.ClassItem)
ci2.subject = c2

ai1 = d.create(diagram.AssociationItem)
ci1.connect_handle(ai1.handles[0])
ci2.connect_handle(ai1.handles[-1])

a1 = ai1.subject
assert a1 is not None

assert len(a1.memberEnd) == 2, a1.memberEnd

ae1, ae2 = a1.memberEnd

d.canvas.update_now()

d.canvas.push_undo()


