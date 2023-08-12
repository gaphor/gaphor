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

Real = EDataType("Real", instanceClassName="double")

String = EDataType("String", instanceClassName="java.lang.String")

UnlimitedNatural = EDataType("UnlimitedNatural", instanceClassName="int")

Boolean = EDataType("Boolean", instanceClassName="boolean")
