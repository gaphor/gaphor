# All model items...
# vim:sw=4

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import inspect
import gobject
import diacanvas

from gaphor.misc import uniqueid
from gaphor.diagram.align import ItemAlign

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


class Relationship(object):
    def __init__(self, head_a = None, head_b = None, tail_a = None, tail_b = None):
        super(Relationship, self).__init__()
        self.head_relation = head_a, head_b
        self.tail_relation = tail_a, tail_b

    # python descriptor protol
    def __get__(self, line, cls):
        if not line:
            return self

        return self.relationship(line)
        

    def __set__(self, line, value):
        pass


    def __delete__(self, line):
        pass


    def relationship(self, line, head_subject = None, tail_subject = None):
        return self.find(line, self.head_relation, self.tail_relation,
                head_subject, tail_subject)


    def find(self, line, head_relation, tail_relation,
            head_subject = None, tail_subject = None):
        """
        Figure out what elements are used in a relationship.
        """

        if not head_subject and not tail_subject:
            head_subject = line.head.connected_to.subject
            tail_subject = line.tail.connected_to.subject

        edge_head_name = head_relation[0]
        node_head_name = head_relation[1]
        edge_tail_name = tail_relation[0]
        node_tail_name = tail_relation[1]

        # First check if the right subject is already connected:
        if line.subject \
                and getattr(line.subject, edge_head_name) is head_subject \
                and getattr(line.subject, edge_tail_name) is tail_subject:
            return line.subject

        # This is the type of the relationship we're looking for
        required_type = getattr(type(tail_subject), node_tail_name).type

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, node_tail_name):
            if not isinstance(gen, required_type):
                continue
                
            gen_head = getattr(gen, edge_head_name)
            try:
                if not head_subject in gen_head:
                    continue
            except TypeError:
                if not gen_head is head_subject:
                    continue

            # check for this entry on line.canvas
            for item in gen.presentation:
                # Allow line to be returned. Avoids strange
                # behaviour during loading
                if item.canvas is line.canvas and item is not line:
                    break
            else:
                return gen
        return None



class DiagramItemMeta(gobject.GObjectMeta):
    """
    Initialize a new diagram item.
    This involves:
    1. registring the new diagram item with the GObject type
    2. If nessesary: add canvas item callbacks
    3. If nessesary: add canvas groupable callbacks
    4. If nessesary: add canvas editable callbacks
    """
    def __new__(self, name, bases, data):

        all_bases = set()
        for base in bases:
            all_bases = all_bases.union(set(inspect.getmro(base)))

        cls = gobject.GObjectMeta.__new__(self, name, bases, data)
        gobject.type_register(cls)

        if (diacanvas.CanvasItem in all_bases) or \
                (diacanvas.CanvasGroup in all_bases) or \
                (diacanvas.CanvasLine in all_bases) or \
                (diacanvas.CanvasElement in all_bases) or \
                (diacanvas.CanvasBox in all_bases) or \
                (diacanvas.CanvasImage in all_bases):
            diacanvas.set_callbacks(cls)

        if diacanvas.CanvasGroupable in all_bases:
            diacanvas.set_groupable(cls)

        if (diacanvas.CanvasEditable in all_bases):
            diacanvas.set_editable(cls)

        # map uml classes to diagram items
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, cls)
            else:
                set_diagram_item(obj, cls)

        return cls


    def __init__(self, name, bases, data):
        # stereotype align information
        align = ItemAlign() # center, top
        align.outside = getattr(self, '__o_align__', False)
        if align.outside:
            align.margin = (0, 2) * 4
        else:
            align.margin = (5, 30) * 2
        self.set_cls_align('s', align, data)


    def set_cls_align(self, kind, align, data):
        assert kind in ('s', 'n')

        hn = '__%s_align__' % kind
        vn = '__%s_valign__' % kind

        if hn in data:
            align.align = data[hn]
        if vn in data:
            align.valign = data[vn]

        setattr(self, '%s_align' % kind, align)



class LineItemMeta(DiagramItemMeta):
    def __new__(cls, name, bases, data):
        item_class = DiagramItemMeta.__new__(cls, name, bases, data)

        # set line relationship
        if '__relationship__' in data:
            rel = data['__relationship__']
            if isinstance(rel, (tuple, set, list)):
                rel = Relationship(*rel)
                item_class.relationship = rel

        # set head and tail handles
        item_class.head = property(lambda self: self.handles[0])
        item_class.tail = property(lambda self: self.handles[-1])

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
