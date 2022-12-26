# Get Started with Gaphor

Gaphor is more than a diagram editor: it's a modeling environment.
Where simple diagram editors such as Microsoft Visio and [draw.io](https://draw.io)
allow you to create pictures, Gaphor actually keeps track of the elements you add
to the model. In Gaphor you can create diagrams to track and visualize different aspects
of the system you're developing.

Enough talk, let's get started.

You can find installers for Gaphor on the [Gaphor website](https://gaphor.org/download). Gaphor can be installed on
Linux (Flatpak, AppImage), Windows, and macOS.

Once Gaphor is launched, it provides you a welcome screen.
It shows you previously openend models and a model templates.

![welcome screen](images/getting-started-greeter.png)

You can select a template to get started.

- **Generic:** (or blank) template
- **UML:** *Unified Modeling Language* template
- **SysML:** *Systems Modeling Language* template
- **RAAML:** *Risk Analysis and Assessment Modeling language* template
- **C4 Model:** *a lean graphical notation technique for modelling the architecture of software systems* template

Once the model interface is loaded you'll see the modeling interface.

![new model](images/getting-started-new-model.png)

The layout of the Gaphor interface is divided into four sections,
namely:

- Navigator
- Diagrams
- Diagram Element Toolbox
- Properties pane

Each section has its own specific function.

## Navigator

The navigator section of the interface displays a hierarchical view of
your model. Every model element you create will be inserted into the
navigator section. This view acts as a tree where you can expand and
collapse different elements of your model. This provides an easy way to
view the elements of your model from an elided perspective. That is, you
can collapse those model elements that are irrelevant to the task at
hand.

In the figure above, you will see that there are three elements in
the navigator view. The root element, _New Model_ is a package. Notice
the small arrow beside _New Model_ that is pointing downward. This
indicates that the element is expanded. You will also notice the two
sub-elements are slightly indented in relation to _New Model_.
The _New Diagram_ element is a diagram.

In the navigator view, you can also right-click the model elements to
get a context menu. This context menu allows you to find out in which
diagram model elements are shown, add new diagrams and packages, and
delete an element.

Double clicking on a diagram element will show it in the Diagram
section. Elements such as classes and packages can be dragged from the
tree view on the diagrams.

## Diagram Section

The diagram section takes up the most space. Multiple diagrams can be
opened at once: they are shown in tabs. Tabs can be closed  by pressing <kbd>Ctrl</kbd>+<kbd>w</kbd>.

Most elements have hot zones. This allows elements to be resized and moved.
Relations (lines-like items) can be commected to

Changes you make can be undone by pressing <kbd>Ctrl</kbd>+<kbd>z</kbd>. To re-do a change, hit
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>z</kbd>.

## Toolbox

The toolbox is mainly used to add new items to a diagram. Select
the element you want to add by clicking on it. When you click on the
diagram, the selected element is created. The arrow is selected again,
so the element can be manipulated.

Tools can be selected by simply clicking on them. By default the pointer
tool is selected after every item placement. This can be changed by
disabling the "Reset tool" option in the Preferences window. Tools can
also be selected by a keyboard shortcut. The actual character is displayed
as part of the tooltip. Finally it is also possible to drag elements on the
canvas from the toolbox.

## Property Editor

The Property Editor is present on the right side of the diagrams.
When no item is selected in the diagram, it shows you some tips and tricks.
When an item is selected on the diagram, it contains the item details.
Things like name, attributes and stereotypes. It can be opened with
<kbd>F9</kbd> and the ![sidebar-show-right-symbolic](images/sidebar-show-right-symbolic.svg) icon in the header bar.

The properties shown depend on the element that is selected.

## Model Preferences

The Property Editor also contains model preferences: Click the ![document-properties-symbolic](images/document-properties-symbolic.svg)
button. Here you can set a few model related settings and edit the [style sheet](style_sheets).
