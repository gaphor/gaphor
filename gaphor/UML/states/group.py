from gaphor.core import gettext
from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import Region, StateMachine, Vertex


@group.register(StateMachine, Vertex)
def state_machine_vertex_group(state_machine, vertex):
    """Add State to a State Machine, add a Region if necessary."""
    if state_machine.region:
        region = state_machine.region[0]
    else:
        region = state_machine.model.create(Region)
        region.name = gettext("Default Region")
        region.stateMachine = state_machine

    vertex.container = region
    return True


@ungroup.register(StateMachine, Vertex)
def state_machine_vertex_ungroup(state_machine, vertex):
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
