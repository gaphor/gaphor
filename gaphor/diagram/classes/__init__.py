from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.generalization import GeneralizationItem
from gaphor.diagram.classes.implementation import ImplementationItem
from gaphor.diagram.classes.interface import InterfaceItem, Folded
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.classes.package import PackageItem


def _load():
    from gaphor.diagram.classes import (
        classconnect,
        interfaceconnect,
        classeseditors,
        classespropertypages,
    )


_load()
