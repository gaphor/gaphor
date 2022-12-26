# Your First Model

```{note}
In this tutorial we refer to the different parts of the gaphor interface:
[Navigator](getting_started:navigator), [Toolbox](getting_started:toolbox),
{ref}`Property Editor <getting_started:property editor>`.

Although the names should speak for themselves, you can check out the [Getting Started](getting_started) page
for more information about those sections.
```

Once Gaphor is started and you can start a new model with the _Generic_ template. The
initial diagram is already open in the Diagram section.

Select an element you want to place, in this case a Class (![new class](../gaphor/ui/icons/hicolor/scalable/actions/gaphor-class-symbolic.svg))
by clicking on the icon in the Toolbox and click on the diagram.
This will place a new Class item instance
on the diagram and add a new Class to the model (it shows up in the Navigator.
The selected tool will reset itself to the Pointer tool after the element is placed
on the diagram.

The Propety Editor on the right side will show you details about the newly added
class, such as its name (_New Class_), attributes and operations (methods).

![image](images/first-model-class.png)

It's simple to add elements to a diagram.

Gaphor does not make any assumptions about which elements should be
placed on a diagram. A diagram is a diagram. UML defines all different
kinds of diagrams, such as Class diagrams, Component diagrams, Action
diagrams, Sequence diagrams. But Gaphor does not place any restrictions.

## Adding Relationships

Add another Class. Change the names to `Shape` and `Circle`. Let's define that `Circle` is a sub-type of `Shape`. You can do this
by selecting one and changing the name in the Property Editor, or by double-clicking the element.

Select Generalization (![new generalization](../gaphor/ui/icons/hicolor/scalable/actions/gaphor-generalization-symbolic.svg)).

Move the mouse cursor over `Shape`. Click, hold and drag the line end over `Circle`. Release the mouse button
and you should have your relationship between `Shape` and `Circle`. You can see both ends of the relation are red,
indicating they are connected to their class.

![image](images/first-model-generalization.png)

Optionally you can run the auto-layouting (![open menu](images/open-menu-symbolic.svg) → Tools → Auto Layout) to align the elements
on the diagram.

## Creating New Diagrams

To create a new diagram, use the Navigator. Select the element that should
contain the new diagram. For now, select _New Model_.
Click the ![new diagram](../gaphor/ui/icons/hicolor/scalable/actions/gaphor-new-diagram-symbolic.svg) in the header bar.

![image](/images/first-model-new-diagram-popup.png)

Select _New Generic Diagram_ and a new diagram is created.

Now drag the elements from the Navigator onto the new diagram. First the classes `Shape` and `Circle`. Add the generalization
last. Drop it somewhere between the two classes. The relation will be created to the diagram.

Now change the name of class `Circle` to `Ellipse`. Check the other diagram. The name has been changed there as well.


```{important}
Elements in a diagram are only a _representation_ of the elements in the underlaying model. The model is what you see in the
Navigator.

Elements in the model are automatically removed when there are no more representations in any of the diagrams.
```
