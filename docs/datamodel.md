# Data Model

Gaphor is an UML tool. In order to keep as close as possible to the UML
specification the Gaphor data model is based on the UML Metamodel. The Object
Management Group (OMG), the not-for-profit technology standards consortium that
governs UML, has a XML Metadata Interchange (XMI) file describing the
metamodel. Therefore, the easiest way to keep Gaphor consistent with UML would
be to to generate Gaphor's data model code directly from this UML metamodel in
XMI. There are two challenges with this approach:

1.  There are more attributes defined in the data model than we will use,
    unless Gaphor got to the point where it 100% implemented the UML specification.
2.  There are no consistency rules in the [UML XMI
definition](https://www.omg.org/spec/UML/20131001/UML.xmi).

The first point ends up not being much of a problem: attributes we don't use
don't consume memory.

For the second point, we have to get the model consistency rules directly from
the [UML Specification](https://www.omg.org/spec/UML/2.5/PDF). Our approach is
to create a special consistency module that checks the model and reports
errors.

In the UML metamodel all classes are derived from `Element`. So we have created
a substitute for `Element` that gives some behaviour to the data objects.

Gaphor's data model is implemented in Python like the rest of the
application. Since the Python language doesn't make a difference between
classes and objects, we can define the possible attributes that an object of
a particular kind can have in a dictionary (name-value map) at class level.
If a value is set, the object checks if an attribute exists in the class'
dictionary (and the parent's dictionary). If the attribute exists, the value
is assigned, if it doesn't exist then an exception is raised.

## Bidirectional References

If two objects need to reference each other, a bidirectional reference
is needed to be supported in Gaphor. This works very similar to the
uni-directional reference that is stored in a dictionary at the class level.
We add some extra information to the dictionary at class
level to make relationship bidirectional. The information is stored in an
extra field that gives us the name of the opposite reference. and voila, we
can create bi-directional references. Please reference
`gaphor/UML/element.py` for more details.

## Implementation

Below is an example of the implementation that allows the user to assign a
value to an instance of `Element` with name `name`. If no value is assigned
before the value is requested, it returns and empty string '':

```python
m = Class()
print(m.name)              # Returns ''
m.name = 'MyName'
print(m.name)              # Returns 'MyName'

m = Element()
c = Comment()
print(m.comment)             # Returns an empty list '[]'
print(c.annotatedElement)    # Returns an empty list '[]'
m.comment = c                # Add 'c' to 'm.comment' and add 'm' to 'c.annotatedElement'
print(m.comment)             # Returns a list '[c]'
print(c.annotatedElement)    # Returns a list '[m]'
```

This behavior is defined in the data model's base class: `Element`. The code
for the data model is stored in uml2.py and is generated from the
`uml2.gaphor` Gaphor model file.

## Extensions to the Data Model

A few changes have been made to Gaphor's implementation of the
metamodel. First of all some relationships have to be modified since the
same name is used for different relationships. Some n:m relationships
have been made 1:n. These are all small changes and should not restrict
the usability of Gaphor's model.

The biggest change is the addition of a whole new class: Diagram.
Diagram is inherited from Namespace and is used to hold a diagram. It
contains a `gaphas.canvas.Canvas` object which can be displayed on
screen by a `DiagramView` class.

## UML.Element

```eval_rst
.. autoclass:: gaphor.core.modeling.Element
```
