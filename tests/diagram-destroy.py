#
# Test the behavior of a UML tree with a Diagram as leaf. The whole tree
# should be freed...
#

import UML
import diagram as dia
import gc

model = UML.Model()
model.name = "MyModel"

package = UML.Package()
package.name = "Package"

model.ownedElement = package
assert len(model.ownedElement.list) == 1
assert model.ownedElement.list[0] is package
assert package.namespace is model

actor = UML.Actor()
actor.namespace = package
assert len(package.ownedElement.list) == 1
assert package.ownedElement.list[0] is actor
assert actor.namespace is package

usecase = UML.UseCase()
usecase.namespace = package
assert len(package.ownedElement.list) == 2
assert package.ownedElement.list[0] is actor
assert package.ownedElement.list[1] is usecase
assert usecase.namespace is package

diagram = dia.Diagram()
diagram.namespace = package
assert len(package.ownedElement.list) == 3
assert package.ownedElement.list[0] is actor
assert package.ownedElement.list[1] is usecase
assert package.ownedElement.list[2] is diagram
assert diagram.namespace is package

diagram.create_item (dia.Actor, pos=(0, 0), subject=actor)
diagram.create_item (dia.UseCase, pos=(100, 100), subject=usecase)

#dia.destroy_diagrams()

model.unlink()
del model
usecase.unlink()
del usecase
actor.unlink()
del actor
package.unlink()
del package
diagram.unlink()
del diagram

gc.collect()
gc.set_debug (gc.DEBUG_LEAK)

print "Uncollectable objects found:", gc.garbage


