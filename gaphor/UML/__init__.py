#
# Gaphor specific extensions for the UML Metamodel.
#
from element import *
from modelelements import *
from elementfactory import *

import libxml2
libxml2.initParser()

#
# A few associations need to be modified to keep the bi-directional aspects
# true (these associations are not well defined in the UML meta model).
#
ClassifierRole._attrdef['message'] = ( Sequence, Message )
#Message._attrdef['receiver'] = ( None, ClassifierRole, 'message' )
#Message._attrdef['sender'] = ( None, ClassifierRole, 'message' )

Instance._attrdef['stimulus'] = ( Sequence, Stimulus )
#Stimulus._attrdef['argument'] = ( Sequence, Instance, 'stimulus' )
#Stimulus._attrdef['sender'] = ( None, Instance, 'stimulus' )
#Stimulus._attrdef['receiver'] = ( None, Instance, 'stimulus' )

Action._attrdef['state'] = ( None, State )
#State._attrdef['exit'] = ( None, Action, 'state' )
#State._attrdef['entry'] = ( None, Action, 'state' )
#State._attrdef['doActivity'] = ( None, Action, 'state' )

# Restrict the usage of a Dependency (and Realization) to one ModelElement
# (The diagram.Dependency class depends on this!)
Dependency._attrdef['client'] = ( None, ModelElement, 'clientDependency' )
Dependency._attrdef['supplier'] = ( None, ModelElement, 'supplierDependency' )

# Some new attribute
#Attribute._attrdef['rawAttribute'] = ( '', String )
#Operation._attrdef['rawOperation'] = ( '', String )
