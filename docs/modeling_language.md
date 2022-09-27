# Modeling Languages

Since version 2.0, Gaphor supports the concept of Modeling languages. This
allows for development of separate modeling languages separate from the Gaphor
core application.

The main language was, and will be UML. Gaphor now also supports a subset of
SysML, RAAML and the C4 model.

A modeling language in Gaphor is defined by a class implementing the
`gaphor.abc.ModelingLanguage` abstract base class. The modeling language should
be registered as a `gaphor.modelinglanguage` entry point.

The `ModelingLanguage` interface is fairly minimal. It allows other services to
look up elements and diagram items, as well as a toolbox, and diagram types.
However, the responsibilities of a modeling language do not stop there. Parts of
functionality will be implemented by registering handlers to a set of generic
functions.

But let's not get ahead of ourselves. What is the functionality a modeling
language implementation can offer?

* A data model (elements) and diagram items
* Diagram types
* A toolbox definition
* [Connectors](#connectors), allow diagram items to connect
* [Copy/paste](#copy-and-paste) behavior when element copying is not trivial,
  for example with more than one element is involved
* [Editor pages](#editor-property-pages), shown in the collapsible pane on the right side
* [Grouping](#grouping), allow elements to be nested in one another
* [Dropping](#dropping), allow elements to be dragged from the tree view onto a diagram
* [Instant (diagram) editor popups](#instant-diagram-editor-popups)
* [Automatic cleanup rules](#automated-model-cleanup) to keep the model consistent

The first three by functionalities are exposed by the `ModelingLanguage` class.
The other functionalities can be extended by adding handlers to the respective
generic functions.


```{eval-rst}
.. autoclass:: gaphor.abc.ModelingLanguage
   :members:
```

## Connectors

Connectors are used to connect one element to another.

Connectors should adhere to the `ConnectorProtocol`.
Normally you would inherit from `BaseConnector`.

```{eval-rst}
.. autoclass:: gaphor.diagram.connectors.BaseConnector
   :members:
```

## Grouping

Grouping is done by dragging one item on top of another, in a diagram or in the tree view.

```{eval-rst}
.. function:: gaphor.diagram.group.group(parent: Element, element: Element) -> bool

   Group an element in a parent element. The grouping can be based on ownership,
   but other types of grouping are also possible.

.. function:: gaphor.diagram.group.ungroup(parent: Element, element: Element) -> bool

   Remove the grouping from an element.
   The function needs to check if the provided `parent` node is the right one.

.. function:: gaphor.diagram.group.can_group(parent_type: Type[Element], element_or_type: Type[Element] | Element) -> bool

   This function tries to determine if grouping is possible,
   without actually performing a group operation.
   This is not 100% accurate.
```

## Dropping

Dropping is performed by dragging an element from the tree view and drop it on a diagram.
This is an easy way to extend a diagram with already existing model elements.

```{eval-rst}
.. function:: gaphor.diagram.drop.drop(element: Element, diagram: Diagram, x: float, y: float) -> Presentation | None

   The drop function creates a new presentation for an element on the diagram.
   For relationships, a drop only works if both connected elements are present in the
   same diagram.

   The big difference with dragging an element from the toolbox, is that dragging from the toolbox
   will actually place a new ``Presentation`` element on the diagram. ``drop`` works the other way
   around: it starts with a model element and creates an accompanying ``Presentation``.
```

## Editor property pages

The editor page is constructed from snippets. For example: almost each element has a name,
so there is a UI snippet that allows you to edit a name.

Each property page (snippet) should inherit from `PropertyPageBase`.

```{eval-rst}
.. autoclass:: gaphor.diagram.propertypages.PropertyPageBase
   :members:
```

## Instant (diagram) editor popups

When you double click on an item in a diagram, a popup can show up so you can easily change the name.

By default this works for any named element. You can register your own inline editor function if you need to.

```{eval-rst}
.. function:: gaphor.diagram.instanteditors.instant_editor(item: Item, view, event_manager, pos: Optional[Tuple[int, int]] = None) -> bool

   Show a small editor popup in the diagram. Makes for
   easy editing without resorting to the Element editor.

   In case of a mouse press event, the mouse position
   (relative to the element) are also provided.
```


## Automated model cleanup

Gaphor wants to keep the model in sync with the diagrams.

A little dispatch function is used to determine if a model element can be removed.

```{eval-rst}
.. function:: gaphor.diagram.deletable.deletable(element: Element) -> bool

   Determine if a model element can safely be removed.
```

## Copy and paste

Copy and paste works out of the box for simple items: one diagram item with one model element (the `subject`).
It leveages the `load()` and `save()` methods of the elements to ensure all relevant data is copied.

Sometimes items need more than one model element to work. For example an Association: it has two association ends.

In those specific cases you need to implement your own copy and paste functions. To create such a thing you'll need to create
two functions: one for copying and one for pasting.

```{eval-rst}
.. function:: gaphor.diagram.copypaste.copy(obj: Element) -> Iterator[tuple[Id, Opaque]]

   Create a copy of an element (or list of elements).
   The returned type should be distinct, so the `paste()`
   function can properly dispatch.

.. function:: gaphor.diagram.copypaste.paste(copy_data: T, diagram: Diagram, lookup: Callable[[str], Element | None]) -> Iterator[Element]

   Paste previously copied data. Based on the data type created in the
   ``copy()`` function, try to duplicate the copied elements.
   Returns the newly created item or element

.. function:: gaphor.diagram.copypaste.paste_link(copy_data: CopyData, diagram: Diagram, lookup: Callable[[str], Element | None]) -> set[Presentation]:

   Create a copy of the Presentation element, but try to link the underlaying model element.
   A shallow copy.

.. function:: gaphor.diagram.copypaste.paste_full(copy_data: CopyData, diagram: Diagram, lookup: Callable[[str], Element | None]) -> set[Presentation]:

   Create a copy of both Presentation and model element. A deep copy.
```

To serialize the copied elements and deserialize them again, there are two functions available:

```{eval-rst}
.. function:: gaphor.diagram.copypaste.serialize(value)

   Return a serialized version of a value. If the ``value`` is an element,
   it's referenced.

.. function:: gaphor.diagram.copypaste.deserialize(ser, lookup)

   Deserialize a value previously serialized with ``serialize()``. The
   ``lookup`` function is used to resolve references to other elements.
```
