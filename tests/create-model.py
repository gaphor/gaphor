#!/usr/bin/env python

# This example creates a model containing a package. In the package are two
# classes, with an association between them.

import sys

sys.path.append("../gmodeler")

import UML

model = UML.Model(1)
model.name = "MyModel"

package = UML.Package(2)
package.name = "MyPackage"

model.ownedElement = package

if __name__ == "__main__":
	print "model = " + str(model)
	print "package = " + str(package)
	print "model.ownedElement = " + str(model.ownedElement.list)
	print "package.namespace = " + str(package.namespace)
	print "==="

klass1 = UML.Class(3)
klass1.name = "MyClass1"
klass2 = UML.Class(4)
klass2.name = "MyClass2"

package.ownedElement = klass1
package.ownedElement = klass2
if __name__ == "__main__":
	print "klass1 = " + str(klass1)
	print "klass2 = " + str(klass2)
	print "package.ownedElement = " + str(package.ownedElement.list)
	print "klass1.namespace = " + str(klass1.namespace)
	print "klass2.namespace = " + str(klass2.namespace)
	print "==="

assend1 = UML.AssociationEnd(5)
assend1.name = "MyAssEnd1"
assend2 = UML.AssociationEnd(6)
assend2.name = "MyAssEnd2"
ass = UML.Association(7)
ass.name = "MyAssociation"

assend1.association = ass
assend2.association = ass
if __name__ == "__main__":
	print "assend1 = " + str(assend1)
	print "assend2 = " + str(assend2)
	print "ass = " + str(ass)
	print "assend1.association = " + str(assend1.association)
	print "assend2.association = " + str(assend2.association)
	print "ass.connection = " + str(ass.connection.list)
	print "==="

# Note: uni-directional (Class -> AssociationEnd)
klass1.association = assend1
klass2.association = assend2
# NOT THIS: assend2.specification = klass2

if __name__ == "__main__":
	print "klass1.association = " + str(klass1.association.list)
	print "klass2.association = " + str(klass2.association.list)
	print "assend1.participant = " + str(assend1.participant)
	print "assend2.participant = " + str(assend2.participant)


# EOF
