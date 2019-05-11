"""
Grouping functionality allows to nest one item within another item (parent
item). This is useful in several use cases

- artifact deployed within a node
- a class within a package or a component
- composite structures (i.e. component within a node)

The grouping adapters has to implement three methods, see `AbstractGroup`
class.

It is important to note, that grouping adapters can be queried before
instance of an item to be grouped is created. This happens when item
is about to be created. Therefore `AbstractGroup.can_contain` has
to be aware that `AbstractGroup.item` can be null.
"""
import logging
import abc

from gaphor import UML
from gaphor.core import inject
from gaphor.misc.generic.multidispatch import multidispatch

log = logging.getLogger(__name__)


@multidispatch(object, object)
class Group:
    def __init__(self, parent, item):
        pass


# TODO: I think this should have been called Namespacing or something similar,
# since that's the modeling concept.
class AbstractGroup(metaclass=abc.ABCMeta):
    """
    Base class for grouping UML objects, i.e.
    interactions contain lifelines and components contain classes objects.

    Base class for grouping UML objects.

    :Attributes:
     parent
        Parent item, which groups other items.
     item
        Item to be grouped.
    """

    element_factory = inject("element_factory")

    def __init__(self, parent, item):
        self.parent = parent
        self.item = item

    def can_contain(self):
        """
        Determine if parent can contain item.
        """
        return True

    @abc.abstractmethod
    def group(self):
        """
        Perform grouping of items.
        """

    @abc.abstractmethod
    def ungroup(self):
        """
        Perform ungrouping of items.
        """


# Until we can deal with types (esp. typing.Any) we use this as a workaround:
@Group.register(None, object)
class NoParentGroup(AbstractGroup):
    def group(self):
        pass

    def ungroup(self):
        pass
