"""
Metaclass item for Metaclass UML metaclass :) from profiles.
"""

from gaphor import UML
from gaphor.diagram.classes import ClassItem
from gaphor.diagram.support import uml


@uml(UML.Component, stereotype="metaclass")
class MetaclassItem(ClassItem):
    pass
