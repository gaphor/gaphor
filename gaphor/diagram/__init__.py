# All model items...
# vim:sw=4

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import gobject
import diacanvas

# Map UML elements to their (default) representation.

import gaphor.UML as UML

_uml_to_item_map = {
#    UML.Actor: ActorItem,
#    UML.Association: AssociationItem,
#    UML.Class: ClassItem,
#    UML.Comment: CommentItem,
#    UML.Dependency: DependencyItem,
#    UML.Generalization: GeneralizationItem,
#    UML.Package: PackageItem,
#    UML.UseCase: UseCaseItem,
}

del UML

def get_diagram_item(element):
    global _uml_to_item_map
    try:
        return _uml_to_item_map[element]
    except:
        return None

def initialize_item(item_class, default_uml_class=None):
    """Initialize a new diagram item.
    This involves:
    1. registring the new diagram item with the GObject type
    2. If nessesary: add canvas item callbacks
    3. If nessesary: add canvas groupable callbacks
    4. If nessesary: add canvas editable callbacks
    """
    global _uml_to_item_map
    gobject.type_register(item_class)
    bases = item_class.__bases__
    if (diacanvas.CanvasItem in bases) or \
	(diacanvas.CanvasGroup in bases) or \
	(diacanvas.CanvasLine in bases) or \
	(diacanvas.CanvasElement in bases) or \
	(diacanvas.CanvasBox in bases) or \
	(diacanvas.CanvasText in bases) or \
	(diacanvas.CanvasImage in bases):
	diacanvas.set_callbacks (item_class)
    if (diacanvas.CanvasGroupable in bases):
	diacanvas.set_groupable (item_class)
    if (diacanvas.CanvasEditable in bases):
	diacanvas.set_editable (item_class)

    if default_uml_class:
	_uml_to_item_map[default_uml_class] = item_class

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
from association import *

