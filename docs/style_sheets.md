# Style Sheets

Since Gaphor 2.0, Gaphor diagrams can have a different look by means of style
sheets. Style sheets use CSS syntax. Since we're dealing with a diagram, and
not a HTML document, some CSS features have been left out.

The style is part of the model, so everyone working on a model will have the
same style.

Here is a simple example of how to change the background color of a class:

``` css
class {
    background-color: beige
}
```

Or change the color of a component, only when it's nested in a node:

``` css
node component {
    background-color: ...
}
```

It's pretty easy to define a "dark" style:

``` css
diagram {
    background-color: black;
}

* {
    color: white
    text-color: white
}
```

Here you already see the first custom attribute: `text-color`. This property
allows you to control the color of the text drawn in an item. `color` is used
for the lines (strokes) that make the layout of a diagram item.

## Supported selectors

We're dealing with diagrams, models. Therefore we do not need all features of
CSS. For example: we do not provide ID's for diagram items, so the CSS syntax
for id's (`#some-id`) is not used. Same for the class syntax (`.some-class`).

```eval_rst
======================= ============================
node component          Any component item which is a decendant of a node.
node > component        A component item which is a child of a node.
generaliation[subject]  A generalization item with a subject present.
class[name=Foo]         A class with name "Foo".
diagram[name^=draft]    A diagram with a name starting with "draft".

                        Other operators include "~=", "$=", "\|=" and "\*=".
\*:focus                The focused item. Other pseudo classes are:

                        - ":active" selected items;
                        - ":hover" for the item under the mouse;
                        - ":drop" if an item is draggen and can be dropped on this item.
node:empty              A node containing no child nodes in the diagram.
:root                   An item is at the top level of the diagram (most items are).
:has()                  ...
:is()                   ...
:not()                  ...
======================= ============================
```

## Style properties

Gaphor supports a subset of CSS properties and some Gaphor specific properties.
The style sheet interpreter is relatively straight forward.


```eval_rst
=================== =================== ================
Property            Type                Note
=================== =================== ================
padding             Padding             CSS style padding
min-width           Number
min-height          Number
line-width          Number
vertical-spacing    Number
border-radius       Number
background-color    Color
font-family         str                 A single font name
font-size           Number
font-style          FontStyle           normal|italic
font-weight         FontWeight          normal|bold
text-decoration     TextDecoration      none|underline
text-align          TextAlign           left|center|right
text-color          Color
color               Color
vertical-align      VerticalAlign       top|middle|bottom
dash-style          Sequence[Number]
highlight-color     Color
line-style          LineStyle           normal|sloppy [factor]
=================== =================== ================
```

Notes:

* `padding` is defined by 1 to 4 numbers. No unit (px, pt, em) needs to be
  used. All values are in pixel distance.
* A color can be any [CSS3 color code](https://www.w3.org/TR/2018/REC-css-color-3-20180619/),
  as described in the CSS documentation. Be it `rgb()`, `rgba()`, Hex code
  (`#ffffff`) or color names.
* `font-family` can be only one font name, not a list of (fallback) names, as
  is used for HTML.
* `dash-style` is a list of numbers (line, gap)
* `line-style` has only effect when defined on a `diagram`. A sloppiness factor
  can be provided, somewhere between -2 and 2.

### Diagram styles

Only a few properties can be defined on a diagram, namely `background-color`
and `line-style`. The diagram style is defined separately from the diagram item
styles. That way it's possible to set the background color for diagrams
specifically. The line style can be normal, straight, lines or a more playful
"sloppy" style. For the sloppy style an optional factor can be provided. This
factor determines the level of wobblyness of the lines. 0.5 is default, 0.0 is
a straight line. The value should be between -2.0 and 2.0. Values between 0.0
and 0.5 make for a subtle effect.
