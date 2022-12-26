---
file_format: mystnb
---

# Example: Gaphor services

In this example we're doing something a little less trivial. In Gaphor, services
are defined as entry points. Each service is a class, and takes parameters with
names that match other services. This allows services to depend on other
services.

It looks something like this:

```{code-cell} ipython3

# entry point name: my_service
class MyService:
    ...

# entry point name: my_other_service
class MyOtherService:
    def __init__(self, my_service):
        ...
```

Let's first load the entry points.

```{code-cell} ipython3
from sphinx.ext.autodoc.mock import mock
from gaphor.entrypoint import load_entry_points


with mock(["gi.repository.Gtk", "gi.repository.Gdk", "gi.repository.GdkPixbuf", "gi.repository.GtkSource", "gi.repository.Adw"]):
    entry_points = load_entry_points("gaphor.services")

entry_points
```

Now let's create a component in our model for every service.

```{code-cell} ipython3
from gaphor import UML
from gaphor.core.modeling import ElementFactory

element_factory = ElementFactory()

def create_component(name):
    c = element_factory.create(UML.Component)
    c.name = name
    return c

components = {name: create_component(name) for name in entry_points}
components
```

With all components mapped, we can create dependencies between those components,
based on the constructor parameter names.

```{code-cell} ipython3
import inspect

for name, cls in entry_points.items():
    for param_name in inspect.signature(cls).parameters:
        if param_name not in components:
            continue

        dep = element_factory.create(UML.Usage)
        dep.client = components[name]
        dep.supplier = components[param_name]
```

With all elements in the model, we can create a diagram. Let's drop the
components and dependencies on the diagram and let auto-layout do its magic.

To make the dependency look good, we have to add a style sheet. If you create a
new diagram via the GUI, this element is automatically added.

```{code-cell} ipython3
from gaphor.core.modeling import Diagram, StyleSheet
from gaphor.diagram.drop import drop

element_factory.create(StyleSheet)
diagram = element_factory.create(Diagram)

for element in element_factory.lselect():
    drop(element, diagram, x=0, y=0)
```

Last step is to layout and draw the diagram.

```{code-cell} ipython3
from gaphor.extensions.ipython import auto_layout, draw

auto_layout(diagram)

draw(diagram, format="svg")
```

That's all. As you can see from the diagram, a lot of services rely on
`EventManager`.
