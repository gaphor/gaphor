# All model items...
# vim:sw=4

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import gobject
import diacanvas
import gaphor.misc.uniqueid as uniqueid

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, uniqueid.generate_id())

def create_as(type, id):
    return type(id)

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

from placementtool import PlacementTool
from actor import ActorItem
from klass import ClassItem
from comment import CommentItem
from commentline import CommentLineItem
from usecase import UseCaseItem
from package import PackageItem
from relationship import RelationshipItem
from dependency import DependencyItem
from generalization import GeneralizationItem
from association import AssociationItem
#import diagramitemactions
import itemactions
