"""
Metaclass item for Metaclass UML metaclass :) from profiles.
"""

from gaphor import UML
from ..classes import ClassItem
from ..support import uml


@uml(UML.Component, stereotype="metaclass")
class MetaclassItem(ClassItem):
    pass
