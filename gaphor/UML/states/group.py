from __future__ import annotations

from gaphor.core import gettext
from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import Region, State, StateMachine, Vertex


@group.register(State, Vertex)
@group.register(StateMachine, Vertex)
def state_machine_vertex_group(state_machine: State | StateMachine, vertex: Vertex):
    """Add State to a State Machine, add a Region if necessary."""
    if state_machine.region:
        region = state_machine.region[0]
    else:
        region = state_machine.model.create(Region)
        region.name = gettext("Default Region")
        state_machine.region = region

    vertex.container = region
    return True


@ungroup.register(State, Vertex)
@ungroup.register(StateMachine, Vertex)
def state_machine_vertex_ungroup(state_machine: State | StateMachine, vertex: Vertex):
    if vertex.container and vertex.container in state_machine.region:
        del vertex.container
        return True
    return False


@group.register(Region, Vertex)
def region_vertex_group(region, vertex):
    vertex.container = region
    return True


@ungroup.register(Region, Vertex)
def region_vertex_ungroup(region, vertex):
    if vertex.container is region:
        del vertex.container
        return True
    return False
