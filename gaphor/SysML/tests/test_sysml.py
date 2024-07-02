from gaphor.SysML import sysml


def test_requirement_traced_to(element_factory):
    req = element_factory.create(sysml.Requirement)
    traced = element_factory.create(sysml.Requirement)
    trace = element_factory.create(sysml.Trace)
    trace.sourceContext = req
    trace.targetContext = traced

    assert traced in req.tracedTo


def test_requirement_derived(element_factory):
    req = element_factory.create(sysml.Requirement)
    derived = element_factory.create(sysml.Requirement)
    trace = element_factory.create(sysml.DeriveReqt)
    trace.sourceContext = req
    trace.targetContext = derived

    assert derived in req.derived


def test_requirement_derived_from(element_factory):
    req = element_factory.create(sysml.Requirement)
    derived = element_factory.create(sysml.Requirement)
    trace = element_factory.create(sysml.DeriveReqt)
    trace.sourceContext = req
    trace.targetContext = derived

    assert req in derived.derivedFrom


def test_requirement_master(element_factory):
    req = element_factory.create(sysml.Requirement)
    copy_req = element_factory.create(sysml.Requirement)
    copy = element_factory.create(sysml.Copy)
    copy.sourceContext = copy_req
    copy.targetContext = req

    assert req in copy_req.master


def test_requirement_refined_by(element_factory):
    req = element_factory.create(sysml.Requirement)
    refined = element_factory.create(sysml.Requirement)
    refine = element_factory.create(sysml.Refine)
    refine.sourceContext = req
    refine.targetContext = refined

    assert refined in req.refinedBy


def test_requirement_satisfied_by(element_factory):
    req = element_factory.create(sysml.Requirement)
    satisfier = element_factory.create(sysml.Requirement)
    satisfy = element_factory.create(sysml.Satisfy)
    satisfy.sourceContext = req
    satisfy.targetContext = satisfier

    assert satisfier in req.satisfiedBy


def test_requirement_verified_by(element_factory):
    req = element_factory.create(sysml.Requirement)
    verifier = element_factory.create(sysml.Requirement)
    verify = element_factory.create(sysml.Verify)
    verify.sourceContext = req
    verify.targetContext = verifier

    assert verifier in req.verifiedBy
