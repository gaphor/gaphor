"""
Package gaphor.diagram.states implements diagram items for UML state machines.

Pseudostates
============
There are some similarities between activities and state machines, for example
    - initial node and initial psuedostate
    - final node and final state
Of course, they differ in many aspects, but the similarities drive user
interface of state machines. This is with respect of minimization of the set
of diagram items (i.e. there is only one diagram item for both join and fork
nodes in activities implemented in Gaphor).

There are separate diagram items for pseudostates
    - initial pseudostate item as there exists initial node item

@todo: Probably, history pseudostates will be implemented as one diagram item
    with an option deep/shallow. [This section is going to be extended as
    we start to implement more pseudostates].
"""

from gaphor.diagram.states.finalstate import FinalStateItem
from gaphor.diagram.states.pseudostates import (
    HistoryPseudostateItem,
    InitialPseudostateItem,
)
from gaphor.diagram.states.state import StateItem
from gaphor.diagram.states.transition import TransitionItem


def _load():
    from gaphor.diagram.states import propertypages, vertexconnect


_load()
