# Modeling Languages

Since version 2.0, Gaphor supports the concept of Modeling languages. This
allows for development of separate modeling languages separate from the Gaphor
core application.

The main language was, and will be UML. Gaphor now also supports a subset of
SysML.

A ModelingLanguage in Gaphor is defined by a class implementing the
`gaphor.abc.ModelingLanguage` abstract base class. The modeling language should
be registered as a `gaphor.modelinglanguage` entry point.

The ModelingLanguage interface is fairly minimal. It allows other services to
look up elements and diagram items, as well as a toolbox. However, the
responsibilities of a ModelingLanguage do not stop there. Parts of
functionality will be implemented by registering handlers to a set of generic
functions.

But let's not get ahead of ourselves. What is the functionality a modeling
language implementation can offer?

* A data model (elements)
* Diagram items
* A toolbox definition
* Connectors, allow diagram items to connect
* Grouping
* Editor pages, shown in the collapsible pane on the right side
* Inline (diagram) editor popups
* Copy/paste behavior when element copying is not trivial, for example with
  more than one element is involved

We expose the first three by methods defined on the ModelingLanguage class. We
then expose the others by adding handlers to the respective generic functions.


```eval_rst
.. autoclass:: gaphor.abc.ModelingLanguage
   :members:
```
