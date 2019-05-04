"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting
 - Editor
   Text editor interface

"""

from functools import singledispatch
from gaphor.misc.generic.multidispatch import multidispatch


@singledispatch
def Editor(obj):
    pass


@multidispatch(object, object)
class Group:
    def __init__(self, parent, item):
        pass


@multidispatch(object, object)
class Group:
    def __init__(self, parent, item):
        pass


@multidispatch(object, object)
class IConnect:
    """
    This function is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def __init__(self, item, line_item):
        pass

    def allow(self, handle, port):
        return False
