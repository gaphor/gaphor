#
# Gaphor specific extensions for the UML Metamodel.
#
from element import *
from modelelements import *
from diagram import *
from elementfactory import *

# Add and extra field to MultiplicityRange, so the range can be added as text:
#MultiplicityRange.__attributes__['range'] = ( '', String )

# Restrict the usage of a Dependency (and Realization) to one ModelElement
# (The diagram.Dependency class depends on this!)
Dependency.__attributes__['client'] = ( None, ModelElement, 'clientDependency' )
Dependency.__attributes__['supplier'] = ( None, ModelElement, 'supplierDependency' )
