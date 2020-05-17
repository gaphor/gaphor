# UML Data Model

Gaphor uses the UML Specification as a guideline for its own data storage.
The Python data model is generated from a Gaphor model file that describes
the relationships between the supported UML elements.

The model is built using smart properties (descriptors). These properties
emit events when they're changed. This allows the rest of the application,
for example, the visuals and undo system, to update their state accordingly.
The events are sent using a signaling mechanism, called handlers.

## Model details

Pay attention to the following changes/additions with respect to the
official Gaphor model, in the `models/UML.gaphor` file:

-   Additions to the model have been put in the package
    AuxiliaryConstructs.Presentations and .Stereotypes.
-   A Diagram element is added in order to model the diagrams.
-   A special construct has been put into place in order to apply
    stereotypes to model elements. The current UML Specification is not
    clear on that subject.
-   The Slot.value reference is singular.
-   ValueSpecification is generated as if it were a normal attribute. As a
    result, its subclasses (Expression, OpaqueExpression, InstanceValue,
    LiteralSpecification and its Literal* subclasses) are not available.
