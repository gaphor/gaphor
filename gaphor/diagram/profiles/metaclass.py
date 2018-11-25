"""
Metaclass item for Metaclass UML metaclass :) from profiles.
"""

from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram import uml
from gaphor import UML


@uml(UML.Component, stereotype="metaclass")
class MetaclassItem(ClassItem):
    pass
