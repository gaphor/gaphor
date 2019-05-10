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
