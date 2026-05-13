import ast
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from gaphor.codegen import ocl


def _extract_ocl_expressions(model: Path) -> list[str]:
    root = ET.parse(model).getroot()

    expressions: list[str] = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "specification":
            continue
        if element.attrib.get("language") != "OCL2.0":
            continue
        body = element.attrib.get("body")
        if body:
            expressions.append(body)

    return expressions


@pytest.mark.parametrize(
    "expression",
    [
        "specializesFromLibrary('Flows::MessageAction')",
        "flowEnd->size() = 2 implies specializesFromLibrary('Flows::Message')",
        "if isNegated then specializesFromLibrary('Requirements::notSatisfiedRequirementChecks') else specializesFromLibrary('Requirements::satisfiedRequirementChecks') endif",
        "subjectParameter = let subjects : OrderedSet(SubjectMembership) = featureMembership->selectByKind(SubjectMembership) in if subjects->isEmpty() then null else subjects->first().ownedSubjectParameter endif",
    ],
)
def test_tokenize_known_expressions(expression):
    result = ocl.tokenize(expression)

    assert result


def test_tokenize_kerml_ocl2_expressions():
    expressions = _extract_ocl_expressions(Path("models/KerML-25-04-04.xmi"))

    assert expressions
    for expression in expressions:
        assert ocl.tokenize(expression)


def test_tokenize_sysml2_ocl2_expressions():
    expressions = _extract_ocl_expressions(Path("models/SysML2-25-02-15.xmi"))

    assert expressions
    for expression in expressions:
        assert ocl.tokenize(expression)


def test_tokenize_range_operator_as_double_dot():
    result = list(ocl.tokenize("Sequence{2..chainingFeature->size()}"))

    assert result == [
        "Sequence",
        "{",
        2,
        "..",
        "chainingFeature",
        "->",
        "size",
        "(",
        ")",
        "}",
    ]


def test_token_stream_current_peek_and_iteration():
    stream = ocl.TokenStream(["a", "+", "b"])

    assert stream.current() == "a"
    assert stream.peek() == "+"
    assert stream.peek(2) == "b"
    assert next(stream) == "a"
    assert stream.current() == "+"
    assert list(stream) == ["+", "b"]
    assert stream.current() is None


def test_parse_simple_identifier():
    result = ocl.parse_to_ast("foo")

    assert isinstance(result, ast.Name)
    assert result.id == "foo"


def test_parse_qualified_name():
    result = ocl.parse_to_ast("Flows::MessageAction")

    assert isinstance(result, ast.Attribute)
    assert result.attr == "MessageAction"
    assert isinstance(result.value, ast.Name)
    assert result.value.id == "Flows"


@pytest.mark.parametrize(
    ("expression", "expected_value"),
    [
        ("'hello'", "hello"),
        ("'it''s'", "it's"),
        ("42", 42),
        ("3.14", 3.14),
    ],
)
def test_parse_constants(expression, expected_value):
    result = ocl.parse_to_ast(expression)

    assert isinstance(result, ast.Constant)
    assert result.value == expected_value


@pytest.mark.parametrize(["token", "value"], [["true", True], ["false", False]])
def test_parse_boolean_literals(token, value):
    true_result = ocl.parse_to_ast(token)

    assert isinstance(true_result, ast.Constant)
    assert true_result.value is value


def test_parse_null_literal():
    result = ocl.parse_to_ast("null")

    assert isinstance(result, ast.Constant)
    assert result.value is None


def test_parse_simple_function_call():
    result = ocl.parse_to_ast("size()")

    assert isinstance(result, ast.Call)
    assert isinstance(result.func, ast.Name)
    assert result.func.id == "size"
    assert result.args == []


def test_parse_function_call_with_args():
    result = ocl.parse_to_ast("contains(item)")

    assert isinstance(result, ast.Call)
    assert isinstance(result.func, ast.Name)
    assert result.func.id == "contains"
    assert len(result.args) == 1
    assert isinstance(result.args[0], ast.Name)
    assert result.args[0].id == "item"


def test_parse_navigation_operation():
    result = ocl.parse_to_ast("list->size()")

    assert isinstance(result, ast.Call)
    assert isinstance(result.func, ast.Attribute)
    assert result.func.attr == "size"
    assert isinstance(result.func.value, ast.Name)
    assert result.func.value.id == "list"


def test_parse_property_access():
    result = ocl.parse_to_ast("object.property")

    assert isinstance(result, ast.Attribute)
    assert result.attr == "property"
    assert isinstance(result.value, ast.Name)
    assert result.value.id == "object"


@pytest.mark.parametrize(
    ("expression", "operator_type"),
    [
        ("a + b", ast.Add),
        ("x - y", ast.Sub),
        ("a * b", ast.Mult),
        ("x / y", ast.Div),
    ],
)
def test_parse_arithmetic_operators(expression, operator_type):
    result = ocl.parse_to_ast(expression)

    assert isinstance(result, ast.BinOp)
    assert isinstance(result.op, operator_type)


def test_parse_operator_precedence():
    result = ocl.parse_to_ast("a + b * c")

    assert isinstance(result, ast.BinOp)
    assert isinstance(result.op, ast.Add)
    assert isinstance(result.right, ast.BinOp)
    assert isinstance(result.right.op, ast.Mult)


@pytest.mark.parametrize(
    ("expression", "operator_type"),
    [
        ("x = y", ast.Eq),
        ("a <> b", ast.NotEq),
        ("x < 10", ast.Lt),
        ("x <= y", ast.LtE),
        ("a > b", ast.Gt),
        ("a >= b", ast.GtE),
    ],
)
def test_parse_comparison_operators(expression, operator_type):
    result = ocl.parse_to_ast(expression)

    assert isinstance(result, ast.Compare)
    assert isinstance(result.ops[0], operator_type)


def test_parse_logical_and():
    result = ocl.parse_to_ast("a and b")

    assert isinstance(result, ast.BoolOp)
    assert isinstance(result.op, ast.And)
    assert len(result.values) == 2


def test_parse_logical_or():
    result = ocl.parse_to_ast("a or b")

    assert isinstance(result, ast.BoolOp)
    assert isinstance(result.op, ast.Or)
    assert len(result.values) == 2


def test_parse_implies():
    result = ocl.parse_to_ast("a implies b")

    assert isinstance(result, ocl.OCLImplies)
    assert isinstance(result.left, ast.Name)
    assert isinstance(result.right, ast.Name)


def test_parse_not():
    result = ocl.parse_to_ast("not x")

    assert isinstance(result, ast.UnaryOp)
    assert isinstance(result.op, ast.Not)


def test_parse_parenthesized_expression():
    result = ocl.parse_to_ast("(a + b) * c")

    assert isinstance(result, ast.BinOp)
    assert isinstance(result.op, ast.Mult)
    assert isinstance(result.left, ast.BinOp)
    assert isinstance(result.left.op, ast.Add)


def test_parse_if_then_else():
    result = ocl.parse_to_ast("if x > 0 then 'positive' else 'negative' endif")

    assert isinstance(result, ast.IfExp)
    assert isinstance(result.test, ast.Compare)
    assert isinstance(result.test.left, ast.Name)
    assert result.test.left.id == "x"
    assert isinstance(result.test.ops[0], ast.Gt)
    assert isinstance(result.test.comparators[0], ast.Constant)
    assert result.test.comparators[0].value == 0
    assert isinstance(result.body, ast.Constant)
    assert result.body.value == "positive"
    assert isinstance(result.orelse, ast.Constant)
    assert result.orelse.value == "negative"


def test_parse_if_then_without_else():
    result = ocl.parse_to_ast("if x then y endif")

    assert isinstance(result, ast.IfExp)
    assert isinstance(result.orelse, ast.Constant)
    assert result.orelse.value is None


def test_parse_let_in():
    result = ocl.parse_to_ast("let x : Integer = 5 in x + 1")

    assert isinstance(result, ocl.OCLLetIn)
    assert result.variable == "x"
    assert result.var_type == "Integer"
    assert isinstance(result.init, ast.Constant)
    assert isinstance(result.body, ast.BinOp)


@pytest.mark.parametrize(
    ("expression", "collection_type", "element_count"),
    [
        ("Set{1, 2, 3}", "Set", 3),
        ("Sequence{a, b}", "Sequence", 2),
        ("OrderedSet{x, y, z}", "OrderedSet", 3),
    ],
)
def test_parse_collections(expression, collection_type, element_count):
    result = ocl.parse_to_ast(expression)

    assert isinstance(result, ocl.OCLCollection)
    assert result.collection_type == collection_type
    assert len(result.elements) == element_count


def test_parse_subscription():
    result = ocl.parse_to_ast("list[0]")

    assert isinstance(result, ast.Subscript)
    assert isinstance(result.value, ast.Name)
    assert result.value.id == "list"


def test_parse_complex_expression():
    expr = "flowEnd->size() = 2 implies specializesFromLibrary('Flows::Message')"
    result = ocl.parse_to_ast(expr)

    assert isinstance(result, ocl.OCLImplies)
    assert isinstance(result.left, ast.Compare)
    assert isinstance(result.right, ast.Call)


def test_parse_real_kerml_expression():
    expressions = _extract_ocl_expressions(Path("models/KerML-25-04-04.xmi"))

    assert expressions

    # Parse a few expressions to AST without errors
    for expression in expressions:
        result = ocl.parse_to_ast(expression)
        assert result is not None


def test_parse_real_sysml2_expression():
    expressions = _extract_ocl_expressions(Path("models/SysML2-25-02-15.xmi"))

    assert expressions

    for expression in expressions:
        result = ocl.parse_to_ast(expression)
        assert result is not None


def test_ast_unparse_capable_with_standard_ast():
    result = ocl.parse_to_ast("a + b")
    unparsed = ast.unparse(result)

    assert "a" in unparsed and "b" in unparsed


def test_lower_to_python_ast_for_implies():
    result = ocl.lower_to_python_ast(ocl.parse_to_ast("a implies b"))

    assert isinstance(result, ast.BoolOp)
    assert isinstance(result.op, ast.Or)
    assert isinstance(result.values[0], ast.UnaryOp)
    assert isinstance(result.values[0].op, ast.Not)
    assert isinstance(result.values[1], ast.Name)
    assert result.values[1].id == "b"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("a + b", "a + b"),
        ("a implies b", "not a or b"),
        ("let x : Integer = 5 in x + 1", "(lambda x: x + 1)(5)"),
        ("Set{1, 2, 3}", "{1, 2, 3}"),
        ("Sequence{a, b}", "[a, b]"),
        ("object.property", "object.property"),
        ("Sequence{2..chainingFeature->size()}", "[range(2, chainingFeature.size())]"),
        (
            "if x > 0 then 'positive' else 'negative' endif",
            "'positive' if x > 0 else 'negative'",
        ),
    ],
)
def test_parse_and_unparse(expression, expected):
    assert ocl.ocl_to_python(expression) == expected


def test_derive_expression():
    result = ocl.ocl_derive_to_python("owner = owningRelationship.owningRelatedElement")

    assert (
        result
        == "lambda e: e.owningRelationship and [e.owningRelationship.owningRelatedElement] or [None]"
    )
