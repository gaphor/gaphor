# UML Datamodel

Gaphor uses the UML metamodel specs as guidelines for its data storage.
In fact, the datamodel is generated for a model file.

The model is built using smart properties (descriptors). Those
descriptors handle events when they\'re changed. This allows the rest of
the application (visuals, undo system) to update their state
accordingly. The events are send using Zope (3)\'s signalling mechanism,
called Handlers.

Model details
=============

Pay attention to the following changes/additions with respect to the
official model:

> -   Additions to the model have been put in the package
>     AuxilaryConstructs.Presentations and .Stereotypes.
> -   A Diagram element is added in order to model the diagrams.
> -   A special construct has been put into place in order to apply
>     stereotypes to model elements. The current specs (2.2) are not
>     clear on that subject.
> -   The Slot.value reference is singular.

::: {.note}
::: {.admonition-title}
Note
:::

ValueSpecification is generated as if it were a normal attribute. As a
result, its subclasses (Expression, OpaqueExpression, InstanceValue,
LiteralSpecification and its Literal\* subclasses) are not available.
:::
