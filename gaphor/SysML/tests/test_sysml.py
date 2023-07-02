from gaphor.SysML import sysml


# sysml.AbstractRequirement.tracedTo = derived('tracedTo', UML.NamedElement, 0, '*', lambda self: [drrp.targetContext for drrp in self.model.select(sysml.DirectedRelationshipPropertyPath) if drrp.targetContext and isinstance(drrp, sysml.Trace)])


def test_requirement_traced_to(element_factory):
    req = element_factory.create(sysml.Requirement)
    traced = element_factory.create(sysml.Requirement)
    trace = element_factory.create(sysml.Trace)
    trace.sourceContext = req
    trace.targetContext = traced

    assert traced in req.tracedTo
