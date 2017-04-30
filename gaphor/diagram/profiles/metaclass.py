"""
Metaclass item for Metaclass UML metaclass :) from profiles.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram import uml
from gaphor.diagram.classes.klass import ClassItem


@uml(uml2.Component, stereotype='metaclass')
class MetaclassItem(ClassItem):
    pass
