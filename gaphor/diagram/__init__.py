# All model items...
# vim:sw=4
from placementtool import *
from actor import *
from klass import *
from comment import *
from commentline import *
from usecase import *
from package import *
from relationship import *
from dependency import *
from generalization import *
#from association import *

# Map UML elements to their (default) representation.

import gaphor.UML as UML

_uml_to_item_map = {
    UML.Actor: ActorItem,
#    UML.Association: AssociationItem,
    UML.Class: ClassItem,
    UML.Comment: CommentItem,
    UML.Dependency: DependencyItem,
    UML.Generalization: GeneralizationItem,
    UML.Package: PackageItem,
    UML.UseCase: UseCaseItem,
}

del UML

def get_diagram_item(element):
    global _uml_to_item_map
    try:
	return _uml_to_item_map[element]
    except:
	return None
