"""
Use case extension relationship.
"""

from gaphor import UML
from gaphor.diagram.usecases.include import IncludeItem


class ExtendItem(IncludeItem):
    """
    Use case extension relationship.
    """

    __uml__ = UML.Extend
    __stereotype__ = "extend"


# vim:sw=4:et
