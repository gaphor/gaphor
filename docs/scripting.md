---
file_format: mystnb
---

# Scripting

One way to work with models is through the GUI. At the poit you’re reading this, you’re may also be interested in getting more out of your models. You like to interact with models through scripts.

You can use scripts to:

* Generate code, as is done for Gaphor’s data model.
* Update a model from another source, like a CSV file.

Since Gaphor is written in Python, it also functions as a library.


## Getting started

To get started, you’ll need a python console. You can use the interactive console in Gaphor,
or install on your host. For the latter, you’ll need a development environment.


## Query a model

A first step is probably to load a model. For this you’ll need an `ElementFactory`. The `ElementFactory` is responsible to creating and maintaining the model. It’s a repository for the model while you’re working on it.

```{code-cell} ipython3
from gaphor.core.modeling import ElementFactory

element_factory = ElementFactory()
```

The module `gaphor.storage` contains everything to load and save models.
Gaphor supports multiple [modeling languages](modeling_language). The `ModelingLanguageService`
consolidates those languages and makes it easy for the loader logic to find
the appropriate classes.

```{note}
In version 2.12 and before an `EventManager` is required. As of Gaphor 2.13, the
`ModelingLanguageService` can be initialized without event manager.
```


```{code-cell} ipython3
from sphinx.ext.autodoc.mock import mock
from gaphor.core.eventmanager import EventManager
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage import storage

event_manager = EventManager()

# Avoid loading of GTK, by using Sphinx’s mock function
with mock(["gi.repository.Gtk", "gi.repository.Gdk"]):
    modeling_language = ModelingLanguageService(event_manager=event_manager)

storage.load(
    "../models/Core.gaphor",
    element_factory,
    modeling_language,
)
```

At this point the model is loaded in the `element_factory` and can be queried.

```{note}
A modeling language consists of the model elements, diagram items and graphical components
required to interact with the elements through the GUI. As a rule of thumb, you’ll need
to have GTK (the GUI toolkit we use) installed to load a full featured modeling language.

One trick to avoid this (when generating Sphinx docs at least) is to use autodoc’s mock function to
mock out the GTK and GDK libraries. Pango needs to be installed for text rendering.
```

A simple query only tells you what elements are in the model. The method `ElementFactory.select()` returns an iterator. Sometimes it’s easier to obtain a list directly. For those cases you can use `ElementFatory.lselect()`.

```{code-cell} ipython3
for element in element_factory.lselect()[:5]:
    print(element)
```

Elements can also be queried by type and with a predicate function:

```{code-cell} ipython3
from gaphor import UML
for element in element_factory.select(UML.Class):
    print(element.name)
```

```{code-cell} ipython3
for diagram in element_factory.select(
    lambda e: isinstance(e, UML.Class) and e.name == "Diagram"
):
    print(diagram)
```

Now, let’s say we want to do some simple (pseudo-)code generation. We can iterate a class’ attributes
and write some output.

```{code-cell} ipython3
diagram: UML.Class

def qname(element):
    return ".".join(element.qualifiedName)

diagram = next(element_factory.select(lambda e: isinstance(e, UML.Class) and e.name == "Diagram"))

print(f"class {diagram.name}({', '.join(qname(g) for g in diagram.general)}):")
for attribute in diagram.attribute:
    if attribute.typeValue:
        # Simple attribute
        print(f"    {attribute.name}: {attribute.typeValue}")
    elif attribute.type:
        # Association
        print(f"    {attribute.name}: {qname(attribute.type)}")
```

To find out which relations can be queried, have a look at the Modeling Language documentation.
Gaphor’s data models have been built using the [UML](models/uml) language.

## Update a model

Updating a model always starts with the element factory: that’s where elements are created.

To create a UML Class instance, you can:

```{code-cell}
my_class = element_factory.create(UML.Class)
my_class.name = "MyClass"
```

To give it an attribute, create an attribute type (`UML.Property`) and provide it some values.

```{code-cell} ipython3
my_attr = element_factory.create(UML.Property)
my_attr.name = "my_attr"
my_attr.typeValue = "string"
my_class.ownedAttribute = my_attr
```

If you save the model, your changes are persisted:

```{code-cell} ipython3
with open("../my-model.gaphor", "w") as out:
    storage.save(out, element_factory)
```
