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
* [Connectors](#connectors), allow diagram items to connect
* [Grouping](#grouping)
* [Editor pages](#editor-property-pages), shown in the collapsible pane on the right side
* [Inline (diagram) editor popups](#inline-diagram-editor-popups)
* [Copy/paste](#copy-and-paste) behavior when element copying is not trivial, for example with
  more than one element is involved

We expose the first three by methods defined on the ModelingLanguage class. We
then expose the others by adding handlers to the respective generic functions.


```eval_rst
.. autoclass:: gaphor.abc.ModelingLanguage
   :members:
```

## Connectors

Connectors are used to connect one element to another.

Connectors should adhere to the `ConnectorProtocol`.
Normally you would inherit from `BaseConnector`.

```eval_rst
.. autoclass:: gaphor.diagram.connectors.BaseConnector
   :members:
```

## Grouping

Grouping is done by dragging one item on top of another.

Grouping dispatch objects are normally inheriting from `AbstractGroup`.

```eval_rst
.. autoclass:: gaphor.diagram.grouping.AbstractGroup
   :members:
```

## Editor property pages

The editor page is constructed from snippets. For example: almost each element has a name,
so there is a UI snippet that allows you to edit a name.

Each property page (snippet) should inherit from `PropertyPageBase`.

```eval_rst
.. autoclass:: gaphor.diagram.propertypages.PropertyPageBase
   :members:
```

## Inline (diagram) editor popups

When you double click on an item in a diagram, a popup can show up so you can easily change the name.

By default this works for any named element. You can register your own inline editor function if you need to.

```eval_rst
.. function:: gaphor.diagram.inlineeditors.InlineEditor(item: Item, view, pos: Optional[Tuple[int, int]] = None) -> bool

   Show a small editor popup in the diagram. Makes for
   easy editing without resorting to the Element editor.

   In case of a mouse press event, the mouse position
   (relative to the element) are also provided.
```


## Copy and paste

Copy and paste works out of the box for simple items: one diagram item with one model element (the `subject`).
It leveages the `load()` and `save()` methods of the elements to ensure all relevant data is copied.

Sometimes items need more than one model element to work. For example an Association: it has two association ends.

In those specific cases you need to implement your own copy and paste functions. To create such a thing you'll need to create
two functions: one for copying and one for pasting.

```eval_rst
.. function:: gaphor.diagram.copypaste.copy(obj: Element) -> T

   Create a copy of an element (or list of elements).
   The returned type should be distinct, so the `paste()`
   function can properly dispatch.

.. function:: gaphor.diagram.copypaste.paste(copy_data: T, diagram: Diagram, lookup: Callable[[str], Element]) -> object

   Paste previously copied data. Based on the data type created in the
   ``copy()`` function, try to duplicate the copied elements.
   Returns the newly created item or element
```

To serialize the copied elements and deserialize them again, there are two functions available:

```eval_rst
.. function:: gaphor.diagram.copypaste.serialize(value)

   Return a serialized version of a value. If the ``value`` is an element,
   it's referenced.

.. function:: gaphor.diagram.copypaste.deserialize(ser, lookup)

   Deserialize a value previously serialized with ``serialize()``. The
   ``lookup`` function is used to resolve references to other elements.
```
