from zope import interface, component

from gaphor.diagram import items
from gaphor.diagram.interfaces import IGroup


###class AdapterMetaclass(type):
###    """
###    Adapter metaclass.
###    """
###    def __new__(self, name, bases, data):
###        """
###        Perform class interface adaptation.
###        """
###
###        import sys
###        frame = sys._getframe(1)
###        locals = frame.f_locals
###
###        cls = type.__new__(self, name, bases, data)
###        if '__adapts__' in data:
###            a, b = data['__adapts__']
###            cls.adapts(a, b)
###            component.provideAdapter(cls)
###
###        return cls
###
###
###    def adapts(self, a, b):
###        """
###        Stolen from zope as component.adapts prevents adapting on metaclass
###        level.
###        """
###        import sys
###        frame = sys._getframe(1)
###        locals = frame.f_locals
###        locals['__component_adapts__'] = component._adapts_descr(a, b)


class AbstractGroup(object):
    """
    Base class for grouping of UML objects.

    Attributes:
     - parent: parent item
     - item:   item to be part of parent item
    """

###    __metaclass__ = AdapterMetaclass

    interface.implements(IGroup)

    def __init__(self, parent, item):
        self.parent = parent
        self.item = item

    def can_contain(self):
        raise NotImplemented, 'This is abstract class'


    def group(self):
        raise NotImplemented, 'This is abstract class'



from gaphor.diagram import DiagramItemMeta
class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """

###    __adapts__ = items.InteractionItem, items.LifelineItem
    def pre_can_contain(self):
        return isinstance(self.parent, items.InteractionItem) \
                and issubclass(self.item, items.LifelineItem)

    def can_contain(self):
        return isinstance(self.parent, items.InteractionItem) \
                and isinstance(self.item, items.LifelineItem)

    def group(self):
        self.parent.subject.lifeline = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)
        #self.parent.add_item(self.item)


    def ungroup(self):
        del self.parent.subject.lifeline[self.item.subject]


component.provideAdapter(factory=InteractionLifelineGroup,
        adapts=(items.InteractionItem, DiagramItemMeta))
component.provideAdapter(factory=InteractionLifelineGroup,
        adapts=(items.InteractionItem, items.LifelineItem))


class ComponentClassGroup(AbstractGroup):
    """
    Add class to component.
    """
