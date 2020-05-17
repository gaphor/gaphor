# Connection Protocol

In Gaphor, if a connection is made on a diagram between an element and a
relationship, the connection is also made at semantic level (the model). From a
GUI point of view, a button release event is what kicks of the decision whether
the connection is allowed. Please reference the page on [Items and
Elements](items.md) if you need a reminder on the difference between the two.

```eval_rst
Is relation with this element allowed?
  No:
    do nothing (not even glue should have happened as the same question is
    asked there).
  Yes:
    connect_handle()
    Is opposite end connected?

      No:
        Do nothing
      Yes:
        Does the item already have a subject element relation?
          Yes:
            Is the previous item the same as the current?
              Yes:
                Do nothing

              No:
                Let subject end point to the new element

          No:
            Create relation or find existing relation in model

            Search for an existing relation in the model:
              Found:
                Use that relation
              Nothing: 
                Create new model elements and connect to item
```

The check if a connection is allowed should also check if it is valid to
create a relation to/from the same element (like associations, but not
generalizations).
