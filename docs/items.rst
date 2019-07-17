Gaphor Diagram Items
====================
The diagram items (or in short `items`) represent UML metamodel on a diagram.
The following sections present the basic items.

DiagramItem
-----------
Basic diagram item supporting item style, text elements and stereotypes.

.. autoclass:: gaphor.diagram.diagramitem.DiagramItem
   :members:

ElementItem
-----------
Rectangular canvas item.

.. autoclass:: gaphor.diagram.elementitem.ElementItem

NamedItem
---------
NamedElement (UML metamodel) representation using rectangular canvas item.

.. autoclass:: gaphor.diagram.nameditem.NamedItem

CompartmentItem
---------------
An item with compartments (i.e. Class or State)

.. autoclass:: gaphor.diagram.compartment.CompartmentItem

ClassifierItem
--------------
Classifer (UML metamodel) representation.

.. autoclass:: gaphor.diagram.classifier.ClassifierItem

FeatureItem
-----------
Diagram representation of UML metamodel classes like property, operation,
stereotype attribute, etc.

.. autoclass:: gaphor.diagram.compartment.FeatureItem


