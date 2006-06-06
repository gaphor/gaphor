"""
Use case extension relationship.
"""

from gaphor import UML
from gaphor.diagram.include import IncludeItem


class ExtendItem(IncludeItem):
    """
    Use case extension relationship.
    """
    __uml__ = UML.Extend
    __relationship__ = 'extendedCase', None, 'extension', 'extend'
    __stereotype__ = 'extend'



# vim:sw=4:et
