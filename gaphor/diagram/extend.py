"""
Use case extension relationship.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.include import IncludeItem


class ExtendItem(IncludeItem):
    """
    Use case extension relationship.
    """
    __uml__ = uml2.Extend
    __stereotype__ = 'extend'



# vim:sw=4:et
