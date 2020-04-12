from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.implementation import ImplementationItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.classes.package import PackageItem


def _load():
    from gaphor.UML.classes import (
        classconnect,
        interfaceconnect,
        classeseditors,
        classespropertypages,
    )


_load()
