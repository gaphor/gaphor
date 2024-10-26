# ruff: noqa: F401,F811
from gaphor import UML
from gaphor.conftest import element_factory, event_manager, modeling_language
from gaphor.core.modeling import Diagram
from gaphor.storage import storage
from gaphor.UML.actions import ActionItem, ControlFlowItem


def test_action_issue(element_factory, modeling_language, test_models):
    """Test an issue when loading a freshly created action diagram."""
    with (test_models / "action-issue.gaphor").open(encoding="utf-8") as f:
        storage.load(f, element_factory, modeling_language)

    actions = element_factory.lselect(UML.Action)
    flows = element_factory.lselect(UML.ControlFlow)
    assert 3 == len(actions)
    assert 3 == len(flows)

    # Actions live in partitions:
    partitions = element_factory.lselect(UML.ActivityPartition)
    assert 2 == len(partitions)

    # Okay, so far the data model is saved correctly. Now, how do the
    # handles behave?
    diagrams = element_factory.lselect(Diagram)
    assert 1 == len(diagrams)

    diagram = diagrams[0]
    assert 7 == len(list(diagram.get_all_items()))
    # Part, Act, Act, Act, Flow, Flow, Flow

    for e in actions + flows:
        assert 1 == len(e.presentation), e
    for i in diagram.select(lambda e: isinstance(e, ControlFlowItem | ActionItem)):
        assert i.subject, i

    # Loaded as:
    #
    # actions[0] --> flows[0, 1]
    # flows[0, 2] --> actions[1]
    # flows[1] --> actions[2] --> flows[2]

    # start element:
    assert actions[0].outgoing[0] is flows[0]
    assert actions[0].outgoing[1] is flows[1]
    assert actions[2].outgoing[0] is flows[2]
    assert not actions[0].incoming

    (cinfo,) = diagram.connections.get_connections(handle=flows[0].presentation[0].head)
    assert cinfo.connected is actions[0].presentation[0]
    (cinfo,) = diagram.connections.get_connections(handle=flows[1].presentation[0].head)
    assert cinfo.connected is actions[0].presentation[0]

    # Intermediate element:
    assert actions[2].incoming[0] is flows[1]
    assert actions[2].outgoing[0] is flows[2]

    (cinfo,) = diagram.connections.get_connections(handle=flows[1].presentation[0].tail)
    assert cinfo.connected is actions[2].presentation[0]
    (cinfo,) = diagram.connections.get_connections(handle=flows[2].presentation[0].head)
    assert cinfo.connected is actions[2].presentation[0]

    # Final element:
    assert actions[1].incoming[0] is flows[0]
    assert actions[1].incoming[1] is flows[2]

    (cinfo,) = diagram.connections.get_connections(handle=flows[0].presentation[0].tail)
    assert cinfo.connected is actions[1].presentation[0]
    (cinfo,) = diagram.connections.get_connections(handle=flows[2].presentation[0].tail)
    assert cinfo.connected is actions[1].presentation[0]

    # Test the parent-child connectivity
    for a in actions:
        (p,) = a.inPartition
        assert p
        assert a.presentation[0].parent
        assert a.presentation[0].parent is p.presentation[0]
