"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting
 - Editor
   Text editor interface

"""

from zope import interface

from functools import singledispatch
from gaphor.misc.generic.multidispatch import multidispatch
import typing


@singledispatch
def Editor(obj):
    pass


@multidispatch(object, object)
class Group(object):
    def __init__(self, parent, item):
        pass


class IConnect(interface.Interface):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    pass
