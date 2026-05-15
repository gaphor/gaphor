from gaphor.codegen.ocl import extract_dependencies_from_ocl


def test_simple_attribute():
    expr = "name"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == {"name"}


def test_chained_attribute():
    expr = "ownedRelationship.ownedRelatedElement"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == {"ownedRelationship.ownedRelatedElement"}


def test_navigation():
    expr = "ownedRelationship->selectByKind(Element)"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == set()


def test_multiple_attributes():
    expr = "a.b + c.d"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == {"a.b", "c.d"}


def test_if_expression():
    expr = "if a then b else c endif"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == {"a", "b", "c"}


def test_rule_constraint():
    expr = "owner = ownedRelationship.ownedRelatedElement"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == {"ownedRelationship.ownedRelatedElement"}


def test_method_call_dependency_uses_receiver_not_method_name():
    expr = "field->method(blah)"
    deps = extract_dependencies_from_ocl(expr)
    assert deps == set()
