#
# GModeler specific extensions for the UML Metamodel.
#
from Element import *
from ModelElements import *

Attribute._attrdef['rawAttribute'] = ( '', String )
Operation._attrdef['rawOperation'] = ( '', String )
