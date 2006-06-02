# All model items...
# vim:sw=4

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import inspect
import gobject
import diacanvas

from gaphor.misc import uniqueid

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, uniqueid.generate_id())

def create_as(type, id):
    return type(id)

def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)

def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item


class DiagramItemMeta(gobject.GObjectMeta):
    """
    Initialize a new diagram item.
    This involves:
    1. registring the new diagram item with the GObject type
    2. If nessesary: add canvas item callbacks
    3. If nessesary: add canvas groupable callbacks
    4. If nessesary: add canvas editable callbacks
    """
    def __new__(cls, name, bases, data):
        all_bases = set()
        for base in bases:
            all_bases = all_bases.union(set(inspect.getmro(base)))

        item_class = gobject.GObjectMeta.__new__(cls, name, bases, data)
        gobject.type_register(item_class)

        if (diacanvas.CanvasItem in all_bases) or \
                (diacanvas.CanvasGroup in all_bases) or \
                (diacanvas.CanvasLine in all_bases) or \
                (diacanvas.CanvasElement in all_bases) or \
                (diacanvas.CanvasBox in all_bases) or \
                (diacanvas.CanvasImage in all_bases):
            diacanvas.set_callbacks(item_class)

        if diacanvas.CanvasGroupable in all_bases:
            diacanvas.set_groupable(item_class)

        if (diacanvas.CanvasEditable in all_bases):
            diacanvas.set_editable(item_class)

        # map uml classes to diagram items
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, item_class)
            else:
                set_diagram_item(obj, item_class)

        return item_class


from nameditem import TextElement
from placementtool import PlacementTool
from classifier import ClassifierItem
from actor import ActorItem
from klass import ClassItem
from comment import CommentItem
from commentline import CommentLineItem
from usecase import UseCaseItem
from package import PackageItem
from interface import InterfaceItem
from relationship import RelationshipItem
from dependency import DependencyItem
from include import IncludeItem
from extend import ExtendItem
from generalization import GeneralizationItem
from implementation import ImplementationItem
from association import AssociationItem
from extension import ExtensionItem
from activitynodes import InitialNodeItem, ActivityFinalNodeItem, FlowFinalNodeItem, DecisionNodeItem, ForkNodeItem
from action import ActionItem
from objectnode import ObjectNodeItem
from flow import FlowItem, CFlowItemA, CFlowItemB
from component import ComponentItem
from connector import ConnectorItem, AssemblyConnectorItem, \
    ConnectorEndItem, ProvidedConnectorEndItem, RequiredConnectorEndItem
from artifact import ArtifactItem
from node import NodeItem
from interaction import InteractionItem
from lifeline import LifelineItem
from message import MessageItem
import itemactions

#if __debug__: 
#    # Keep track of all model elements that are created
#    from gaphor.misc.aspects import ReferenceAspect, weave_method
#    from gaphor import refs
#    weave_method(create_as, ReferenceAspect, refs)
