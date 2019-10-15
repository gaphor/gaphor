# Connection Protocol

In Gaphor, if a connection is made on a diagram between an element and a
relationship, the connection is also made at semantic level (the model).
From a GUI point of view it all starts with a button release event.

With \"item\" I refer to objects in a diagram (graphical), with
\"element\" I refer to semantic (model) objects.

Is relation with this element allowed?

:   

    No:

    :   do nothing (not even glue should have happened as the same
        question is asked there).

    Yes:

    :   connect\_handle() Is opposite end connected?

        > No:
        >
        > :   Do nothing
        >
        > Yes:
        >
        > :   
        >
        >     Does the item already have a subject element relation?
        >
        >     :   
        >
        >         Yes:
        >
        >         :   
        >
        >             Is the previous item the same as the current?
        >
        >             :   
        >
        >                 Yes:
        >
        >                 :   Do nothing
        >
        >                 No:
        >
        >                 :   Let subject end point to the new element
        >
        >         No:
        >
        >         :   Create relation or find existing relation in model
        >
        >             Search for an existing relation in the model:
        >
        >             :   
        >
        >                 Found:
        >
        >                 :   
        >
        >                     Use that relation
        >
        >                     :   Nothing:
        >
        >             Create new model elements and connect to item
        >
The check if a connection is allowed should also check if it is valid to
create a relation to/from the same element (like associations, but not
generalizations)
