"""Definition of meta model 'uml_types'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import EDataType, EPackage


name = "uml_types"
nsURI = "https://www.omg.org/spec/UML/20161101/PrimitiveTypes"
nsPrefix = "primitives"

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}  # type: ignore
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)

Integer = EDataType("Integer", instanceClassName="int")
Integer.from_string = lambda x: int(x)

Real = EDataType("Real", instanceClassName="double")
Real.from_string = lambda x: float(x)

String = EDataType("String", instanceClassName="java.lang.String")

UnlimitedNatural = EDataType("UnlimitedNatural", instanceClassName="int")


def unlimited_from_string(x):
    if x == "*":
        return -1
    value = int(x)
    if value >= 0:
        return value
    raise ValueError("UnlimitedNatural must be a >= 0 value")


UnlimitedNatural.from_string = unlimited_from_string
UnlimitedNatural.to_string = lambda x: "*" if x < 0 else str(x)

Boolean = EDataType("Boolean", instanceClassName="boolean")
Boolean.to_string = lambda x: str(x).lower()
Boolean.from_string = lambda x: x in ["True", "true"]
