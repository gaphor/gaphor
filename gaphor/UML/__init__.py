#
# GModeler specific extensions for the UML Metamodel.
#
from Element import *
from ModelElements import *
from management import *

# Make the relationship ends bi-directional, so we can easely connect and
# disconnect them...
#Generalization._attrdef['parent'] = ( None, GeneralizableElement, 'specialization' )
#Dependency._attrdef['supplier'] = ( Sequence, ModelElement, 'supplierDependency' )
#Extend._attrdef['base'] = ( None, UseCase, 'extender' )
#Include._attrdef['addition'] = ( None, UseCase, 'includer' )

# Hacks to make the meta model work properly...
Namespace._attrdef['ownedElement'] = ( Sequence, ModelElement, 'namespace' )
ModelElement._attrdef['namespace'] = ( None, Namespace, 'ownedElement' )

Association._attrdef['connection'] = ( Sequence, AssociationEnd, 'association' )
AssociationEnd._attrdef['association'] = ( None, Association, 'connection' )

ClassifierRole._attrdef['message'] = ( Sequence, Message )
#Message._attrdef['receiver'] = ( None, ClassifierRole )
#Message._attrdef['sender'] = ( None, ClassifierRole )

#del Instance._attrdef['stimulus']
Instance._attrdef['stimulus'] = ( Sequence, Stimulus )
#Stimulus._attrdef['argument'] = ( Sequence, Instance )
#Stimulus._attrdef['receiver'] = ( None, Instance )


# Some new attribute
#Attribute._attrdef['rawAttribute'] = ( '', String )
#Operation._attrdef['rawOperation'] = ( '', String )
