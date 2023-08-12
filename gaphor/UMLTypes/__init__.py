from gaphor.UMLTypes.uml_types import eClassifiers
from gaphor.UMLTypes.uml_types import eClass
from gaphor.UMLTypes.uml_types import Integer, Real, String, UnlimitedNatural, Boolean

from gaphor.UMLTypes import uml_types

__all__ = ["Integer", "Real", "String", "UnlimitedNatural", "Boolean"]

otherClassifiers = [Integer, Real, String, UnlimitedNatural, Boolean]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)
