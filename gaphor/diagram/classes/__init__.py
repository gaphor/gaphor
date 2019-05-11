from .association import AssociationItem
from .dependency import DependencyItem
from .generalization import GeneralizationItem
from .implementation import ImplementationItem
from .interface import InterfaceItem
from .klass import ClassItem
from .package import PackageItem


def _load():
    from . import classconnect, interfaceconnect, classespropertypages


_load()
