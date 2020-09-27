# Connection Protocol

In Gaphor, if a connection is made on a diagram between an element and a
relationship, the connection is also made at semantic level (the model). From a
GUI point of view, a button release event is what kicks of the decision whether
the connection is allowed. Please reference the page on [Items and
Elements](items.md) if you need a reminder on the difference between the two.

![connection chart](connect/main.svg)

The check if a connection is allowed should also check if it is valid to
create a relation to/from the same element (like associations, but not
generalizations).
