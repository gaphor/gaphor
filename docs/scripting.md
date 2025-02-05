---
file_format: mystnb
---

# Jupyter and Scripting

One way to work with models is through the GUI. However, you may also be
interested in getting more out of your models by interacting with them through
Python scripts and [Jupyter notebooks](https://jupyter.org/).

You can use scripts to:

* Explore the model, check for (in)valid conditions.
* Generate code, as is done for Gaphor’s data model.
* Update a model from another source, like a CSV file.

Since Gaphor is written in Python, it also functions as a library.

## Getting started

To get started, you’ll need a Python console. You can use the interactive
console in Gaphor, use a Jupyter notebook, although that will require setting
up a Python development environment.

## Query a model

The first step is to load a model. For this you’ll need an
{obj}`gaphor.core.modeling.ElementFactory`. The
`ElementFactory` is responsible to creating and maintaining the model. It acts
as a repository for the model while you’re working on it.

```{code-cell} ipython3
from gaphor.core.modeling import ElementFactory

element_factory = ElementFactory()
```

The module `gaphor.storage` contains everything to load and save models. Gaphor
supports multiple [modeling languages](modeling_language). The
`ModelingLanguageService` consolidates those languages and makes it easy for the
loader logic to find the appropriate classes.

```{note}
In versions before 2.13, an `EventManager` is required. In later versions, the
`ModelingLanguageService` can be initialized without event manager.
```


```{code-cell} ipython3
:tags: [remove-stderr]

from gaphor.core.eventmanager import EventManager
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage import storage

event_manager = EventManager()

modeling_language = ModelingLanguageService(event_manager=event_manager)

with open("../models/Core.gaphor", encoding="utf-8") as file_obj:
    storage.load(
        file_obj,
        element_factory,
        modeling_language,
    )
```

At this point the model is loaded in the `element_factory` and can be queried.

```{note}
A modeling language consists of the model elements, and diagram items.
Graphical components are loaded separately.
For the most basic manupilations, GTK (the GUI toolkit we use) is not required,
but you may run into situations where Gaphor tries to load the GTK library.

One trick to avoid this (when generating Sphinx docs at least) is to use
autodoc’s mock function to mock out the GTK and GDK libraries. However, Pango
needs to be installed for text rendering.
```

A simple query only tells you what elements are in the model. The method
`ElementFactory.select()` returns an iterator. Sometimes it’s easier to obtain a
list directly. For those cases you can use `ElementFatory.lselect()`. Here we
select the last five elements:

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

Now, let’s say we want to do some simple (pseudo-)code generation. We can
iterate class attributes and write some output.

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

To find out which relations can be queried, have a look at the [modeling
language](modeling_language) documentation. Gaphor’s data models have been built
using the [UML](models/uml) language.

You can find out more about a model property by printing it.

```{code-cell} ipython3
print(UML.Class.ownedAttribute)
```

In this case it tells us that the type of `UML.Class.ownedAttribute` is
`UML.Property`. `UML.Property.class_` is set to the owner class when
`ownedAttribute` is set. It is a bidirectional relation.

## Draw a diagram

Another nice feature is drawing the diagrams. At this moment this requires a
function. This behavior is similar to the [`diagram` directive](sphinx).

```{code-cell} ipython3
from gaphor.core.modeling import Diagram
from gaphor.extensions.ipython import draw

d = next(element_factory.select(Diagram))
draw(d, format="svg")
```

## Create a diagram

(Requires Gaphor 2.13)

Now let's make something a little more fancy. We still have the core model
loaded in the element factory. From this model we can create a custom diagram.
With a little help of the auto-layout service, we can make it a readable
diagram.

To create the diagram, we [`drop` elements](modeling_language:dropping) on the
diagram. Items on a diagram represent an element in the model. We'll also drop
all associations on the model. Only if both ends can connect, the association
will be added.

```{code-cell} ipython3
from gaphor.diagram.drop import drop
from gaphor.extensions.ipython import auto_layout

temp_diagram = element_factory.create(Diagram)

for name in ["Presentation", "Diagram", "Base"]:
    element = next(element_factory.select(
        lambda e: isinstance(e, UML.Class) and e.name == name
    ))
    drop(element, temp_diagram, x=0, y=0)

# Drop all assocations, see what sticks
for association in element_factory.lselect(UML.Association):
    drop(association, temp_diagram, x=0, y=0)

auto_layout(temp_diagram)

draw(temp_diagram, format="svg")
```

The diagram is not perfect, but you get the picture.

## Update a model

Updating a model always starts with the element factory: that’s where elements
are created.

To create a UML Class instance, you can:

```{code-cell}
my_class = element_factory.create(UML.Class)
my_class.name = "MyClass"
```

To give it an attribute, create an attribute type (`UML.Property`) and then
assign the attribute values.

```{code-cell} ipython3
my_attr = element_factory.create(UML.Property)
my_attr.name = "my_attr"
my_attr.typeValue = "string"
my_class.ownedAttribute = my_attr
```

Adding it to the diagram looks like this:

```{code-cell} ipython3
my_diagram = element_factory.create(Diagram)
drop(my_class, my_diagram, x=0, y=0)
draw(my_diagram, format="svg")
```

If you save the model, your changes are persisted:

```{code-cell} ipython3
model_filename = "../my-model.gaphor"
with open(model_filename, "w") as out:
    storage.save(out, element_factory)
```

### Updating elements

If you need to update existing elements, this can be done by keeping track of the element ID. Each element in the model
has a unique internal id. Once again we need some imports from Gaphor:

```{code-cell} ipython3
from pathlib import Path

from gaphor import UML
from gaphor import SysML
from gaphor.application import Session  # needed to run services
from gaphor.transaction import Transaction  # needed to make changes
from gaphor.storage import storage  # needed to save to file
```

Then start up the services we will use:

```{code-cell} ipython3
session = Session(
    services=[
        "event_manager",
        "component_registry",
        "element_factory",
        "element_dispatcher",
        "modeling_language",
    ]
)

# Get services we need.
element_factory = session.get_service("element_factory")
modeling_language = session.get_service("modeling_language")
event_manager = session.get_service("event_manager")
```

and load in the model to the session

```{code-cell} ipython3
with open(model_filename, encoding="utf-8") as file_obj:
    storage.load(
        file_obj,
        element_factory,
        modeling_language,
    )

# Now we query the model to get the element we want to change:
the_class = next(
    element_factory.select(
        lambda e: isinstance(e, UML.Class) and e.name == "MyClass"
    ))
```

Importantly, the changes are made as part of a `Transaction`. Here we find the element with the same id, and then update
the content. We then save the altered model to a file.

```{code-cell} ipython3
# change the name and write back into the model
with Transaction(event_manager) as ctx:
    the_class.name = "Not My Class Anymore"
    the_class.ownedAttribute[0].typeValue = "updated string"

# Write changes to file here
with open(model_filename, "w") as out:
    storage.save(out, element_factory)

```

## What else

What else is there to know…

* Gaphor supports derived associations. For example, `element.owner` points to the owner element. For an attribute that would be its containing class.
* The module `gaphor.UML.recipes` contains several functions for manipulating elements and their associations.
* The tests for a given modelling language are a good place to find reference examples of element creation and modification.
* All data models are described in the `Modeling Languages` section of the docs.
* If you use Gaphor’s Console, you’ll need to apply all changes in a transaction, or they will result in an error.
* If you want a comprehensive example of a code generator, have a look at [Gaphor’s `coder` module](https://github.com/gaphor/gaphor/blob/main/gaphor/codegen/coder.py). This module is used to generate the code for the data models used by Gaphor.
* This page is rendered with [MyST-NB](https://myst-nb.readthedocs.io/). It’s actually a Jupyter Notebook!

## Examples

Expanding on the information above the following snippetts show how to create requirements and interfaces.

### Requirements from text fields

```{code-cell} ipython3
txts = ['req1', 'req2', 'bob the cat']
outfile = "requirement_example.gaphor"
with Transaction(event_manager) as ctx:
    my_diagram = element_factory.create(Diagram)
    my_diagram.name= 'my diagram'
    reqPackage = element_factory.create(UML.Package)
    reqPackage.name = "Requirements"
    drop(reqPackage, my_diagram, x=0, y=0)


    for req_id,txt in enumerate(txts):
        my_class = element_factory.create(SysML.sysml.Requirement)
        my_class.name = f"{req_id}-{txt[:3]}"
        my_class.text = f"{txt}"
        my_class.externalId = f"{req_id}"

        drop(my_class, my_diagram, x=0, y=0)

    # Save the model or export diagrams.

```

### Interfaces from dictionaries

```{code-cell} ipython3
# get interface definitions from file into this dictionary format
interfaces = {'Interface1': ['signal1:type1', 'signal2:type1', 'signal3:type1'],
              'Interface2': ['signal4:type2', 'signal5:type2', 'signal6:type2']}
outfile = 'interface_example.gaphor'
with Transaction(event_manager) as ctx:
    my_diagram = element_factory.create(UML.Diagram)
    my_diagram.name=' my diagram'
    intPackage = element_factory.create(UML.Package)
    intPackage.name = "Interfaces"
    drop(intPackage, my_diagram, x=0, y=0)


    for interface,signals in interfaces.items():
        my_class = element_factory.create(UML.uml.Interface)
        my_class.name = f"{interface}"
        for s in signals:
            my_attr = element_factory.create(UML.Property)
            name,vtype = s.split(':')
            my_attr.name = name
            my_attr.typeValue = vtype
            my_class.ownedAttribute = my_attr

        drop(my_class, my_diagram, x=0, y=0)


    # Save the model or export diagrams.
```

### Basic Validation
Some simple validation checks can be run using a couple of small functions to select and evaluate elements.

```{code-cell} ipython3

# As before assume we have a factory service and the model is loaded
# Define a function to select an element
def element_select(element):
    return isinstance(element, UML.Class)


# Define a validation rule - names must be capatalised
def rule(element):
    return element.name[0].isupper()


# Define a message to display if the element fails the validation
msg = "Class Names must be capitalised"

element = next(element_factory.select(element_select))
is_valid = rule(element)
if not is_valid:
    print(msg)
```

Here is another example:

```{toctree}
gaphor-services
```
