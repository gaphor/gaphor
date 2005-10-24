from gaphor import resource
from gaphor import UML

node_classes = {
    UML.ForkNode:     UML.JoinNode,
    UML.DecisionNode: UML.MergeNode,
    UML.JoinNode:     UML.ForkNode,
    UML.MergeNode:    UML.DecisionNode,
}

def move_collection(src, target, name):
    """
    Copy collection from one object to another.

    src    - source object
    target - target object
    name   - name of attribute, which is collection to copy
    """
    # first make of copy of collection, because assigning
    # element to target collection moves this element
    for flow in list(getattr(src, name)):
        getattr(target, name).append(flow)


def is_fd(node):
    """
    Check if node is fork or decision node.
    """
    return isinstance(node, (UML.ForkNode, UML.DecisionNode))


def change_node_class(node):
    """
    If UML constraints for fork, join, decision and merge nodes are not
    met, then create new node depending on input node class, i.e. create
    fork node from join node or merge node from decision node.

    If constraints are met, then return node itself.
    """
    if is_fd(node) and len(node.incoming) > 1 \
            or not is_fd(node) and len(node.incoming) < 2:

        factory = resource(UML.ElementFactory)
        cls = node_classes[node.__class__]
        log.debug('creating %s' % cls)
        nn = factory.create(cls)
        move_collection(node, nn, 'incoming')
        move_collection(node, nn, 'outgoing')
    else:
        nn = node

    assert nn is not None

    # we have to accept zero of outgoing edges in case of fork/descision
    # nodes
    assert is_fd(nn) and len(nn.incoming) <= 1 \
        or not is_fd(nn) and len(nn.incoming) >= 1, '%s' % nn
    assert is_fd(nn) and len(nn.outgoing) >= 0 \
        or not is_fd(nn) and len(nn.outgoing) <= 1, '%s' % nn
    return nn


def combine_nodes(node):
    """
    Create fork/join (decision/merge) nodes combination as described in UML
    specification.
    """
    log.debug('combining nodes')

    cls = node_classes[node.__class__]
    log.debug('creating %s' % cls)
    factory = resource(UML.ElementFactory)
    target = factory.create(cls)

    source = node
    if is_fd(node):
        source = target
        move_collection(node, source, 'incoming')

        # create new fork node
        cls = node_classes[source.__class__]
        log.debug('creating %s' % cls)
        target = factory.create(cls)
        move_collection(node, target, 'outgoing')
    else:
        # fork node is created, referenced by target
        move_collection(source, target, 'outgoing')

    assert not is_fd(source)
    assert is_fd(target)

    # create flow
    c1 = count_object_flows(source, 'incoming')
    c2 = count_object_flows(target, 'outgoing')

    if c1 > 0 or c2 > 0:
        flow = factory.create(UML.ControlFlow)
    else:
        flow = factory.create(UML.ObjectFlow)
    flow.source = source
    flow.target = target

    assert len(source.incoming) > 1
    assert len(source.outgoing) == 1

    assert len(target.incoming) == 1
    assert len(target.outgoing) > 1

    return source


def decombine_nodes(source):
    """
    Create node depending on source argument which denotes combination of
    fork/join (decision/merge) nodes as described in UML specification.

    Combination of nodes is destroyed.
    """
    log.debug('decombining nodes')
    flow = source.outgoing[0]
    target = flow.target

    if len(source.incoming) < 2:
        # create fork or decision
        cls = target.__class__
    else:
        # create join or merge
        cls = source.__class__

    factory = resource(UML.ElementFactory)
    node = factory.create(cls)

    move_collection(source, node, 'incoming')
    move_collection(target, node, 'outgoing')

    assert source != node

    # delete target and combining flow
    # source should be deleted by caller
    target.unlink()
    flow.unlink()

    # return new node
    return node


def determine_node_on_connect(el):
    """
    Determine classes of nodes depending on amount of incoming
    and outgoing edges. This method is called when flow is attached
    to node.

    If there is more than one incoming edge and more than one
    outgoing edge, then create two nodes and combine them with
    flow as described in UML specification.
    """
    subject = el.subject
    if not isinstance(subject, tuple(node_classes.keys())):
        return

    new_subject = subject

    if len(subject.incoming) > 1 and len(subject.outgoing) > 1:
        new_subject = combine_nodes(subject)
        el.combined = True

    else:
        new_subject = change_node_class(subject)

    if el.combined:
        check_combining_flow(el)

    change_node_subject(el, new_subject)


def determine_node_on_disconnect(el):
    """
    Determine classes of nodes depending on amount of incoming
    and outgoing edges. This method is called when flow is dettached
    from node.

    If there are combined nodes and there is no need for them, then replace
    combination with appropriate node (i.e. replace with fork node when
    there are less than two incoming edges). This way data model is kept as
    simple as possible.
    """
    subject = el.subject
    if not isinstance(subject, tuple(node_classes.keys())):
        return

    new_subject = subject

    if el.combined:
        cs = subject.outgoing[0].target
        if len(subject.incoming) < 2 or len(cs.outgoing) < 2:
            new_subject = decombine_nodes(subject)
            el.combined = False
        else:
            check_combining_flow(el)

    else: 
        new_subject = change_node_class(subject)

    change_node_subject(el, new_subject)


def change_node_subject(el, new_subject):
    """
    Change element's subject if new subject is different than element's
    subject. If subject is changed, then old subject is destroyed.
    """
    subject = el.subject
    if new_subject != subject:
        log.debug('changing subject of ui node %s' % el)
        el.set_subject(new_subject)

        log.debug('deleting node %s' % subject)
        subject.unlink()


def create_flow(cls, flow):
    """
    Create new flow of class cls. Flow data from flow argument are copied
    to new created flow. Old flow is destroyed.
    """
    factory = resource(UML.ElementFactory)
    f = factory.create(cls)
    f.source = flow.source
    f.target = flow.target
    flow.unlink()
    return f


def count_object_flows(node, attr):
    """
    Count incoming or outgoing object flows.
    """
    return len(getattr(node, attr)
        .select(lambda flow: isinstance(flow, UML.ObjectFlow)))


def check_combining_flow(el):
    """
    Set object flow as combining flow when incoming or outgoing flow count
    is greater than zero. Otherwise change combining flow to control flow.
    """
    subject = el.subject
    flow = subject.outgoing[0] # combining flow
    combined = flow.target     # combined node

    c1 = count_object_flows(subject, 'incoming')
    c2 = count_object_flows(combined, 'outgoing')

    log.debug('combined incoming and outgoing object flow count: (%d, %d)' % (c1, c2))

    if (c1 > 0 or c2 > 0) and isinstance(flow, UML.ControlFlow):
        log.debug('changing combing flow to object flow')
        create_flow(UML.ObjectFlow, flow)
    elif c1 == 0 and c2 == 0 and isinstance(flow, UML.ObjectFlow):
        log.debug('changing combing flow to control flow')
        create_flow(UML.ControlFlow, flow)
