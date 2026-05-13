"""OCL 2.0 parser

The parser is limited, in that it is only capable of producing
Python expressions (lambda functions) for a small part of the
OCL expressions present in the KerML and SysML v2 models.

It should be enough to generate the data model, though.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast

from pyparsing import (
    Combine,
    Literal,
    MatchFirst,
    ParserElement,
    ParseResults,
    QuotedString,
    Regex,
    StringEnd,
    StringStart,
    Word,
    alphanums,
    alphas,
    pyparsing_common,
)

from gaphor import UML

ParserElement.enable_packrat()


# Custom AST node types for OCL-specific constructs
@dataclass
class OCLNavigation:
    """Represents OCL navigation: expr->operation() or expr.property"""

    target: ASTNode
    operator: str  # "->" or "."
    property_name: str


@dataclass
class OCLLetIn:
    """Represents OCL let-in expression: let var : Type = expr in expr"""

    variable: str
    var_type: str | None
    init: ASTNode
    body: ASTNode


@dataclass
class OCLCollection:
    """Represents OCL collection: Set{...}, Sequence{...}, OrderedSet{...}"""

    collection_type: str
    elements: list[ASTNode]


@dataclass
class OCLImplies:
    """Represents OCL implies operator: expr implies expr"""

    left: ASTNode
    right: ASTNode


# Type alias for all possible AST nodes
ASTNode = ast.expr | OCLNavigation | OCLLetIn | OCLCollection | OCLImplies
Token = str | int | float


def _build_tokenizer() -> ParserElement:
    # OCL identifiers and qualified names are permissive in practice.
    identifier = Word(alphas + "_$", alphanums + "_$")
    qualified_identifier = Combine(identifier + Literal("::") + identifier)

    string_literal = QuotedString("'", esc_quote="''", unquote_results=False)
    float_number = Regex(r"\d+\.\d+").set_parse_action(lambda tokens: float(tokens[0]))
    integer_number = pyparsing_common.integer()
    number = float_number | integer_number

    operators = MatchFirst(
        [
            Literal("->"),
            Literal("::"),
            Literal("<="),
            Literal(">="),
            Literal("<>"),
            Literal(".."),
            Literal("="),
            Literal("<"),
            Literal(">"),
            Literal("+"),
            Literal("-"),
            Literal("*"),
            Literal("/"),
            Literal("."),
            Literal("|"),
            Literal(","),
            Literal(":"),
            Literal(";"),
            Literal("("),
            Literal(")"),
            Literal("["),
            Literal("]"),
            Literal("{"),
            Literal("}"),
        ]
    )

    # Keep parsing permissive for generated/migrated OCL that may contain typos.
    unknown = Regex(r"\S")

    token = (
        string_literal
        | number
        | qualified_identifier
        | identifier
        | operators
        | unknown
    )

    return cast(ParserElement, StringStart() + token[...] + StringEnd())


OCL_TOKENIZER = _build_tokenizer()


def tokenize(expression: str) -> ParseResults:
    return OCL_TOKENIZER.parse_string(expression, parse_all=True)


class TokenStream:
    """Iterate over tokens while still allowing current-token inspection."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def __iter__(self) -> TokenStream:
        return self

    def __next__(self) -> Token:
        token = self.consume()
        if token is None:
            raise StopIteration
        return token

    def current(self) -> Token | None:
        return self.peek(0)

    def peek(self, offset: int = 1) -> Token | None:
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else None

    def consume(self) -> Token | None:
        token = self.current()
        if token is not None:
            self.pos += 1
        return token


def _coerce_expr(node: ASTNode, operator: str | Token | None) -> ast.expr:
    if isinstance(node, ast.expr):
        return node

    try:
        return lower_to_python_ast(node)
    except TypeError as exc:
        msg = f"Unsupported operand for {operator}: {type(node).__name__}"
        raise ValueError(msg) from exc


def _parse_expression(stream: TokenStream) -> ASTNode:
    return _parse_logical_or(stream)


def _parse_logical_or(stream: TokenStream) -> ASTNode:
    left = _parse_logical_and(stream)

    while stream.current() == "or":
        stream.consume()
        right = _parse_logical_and(stream)
        left = ast.BoolOp(
            op=ast.Or(),
            values=[_coerce_expr(left, "or"), _coerce_expr(right, "or")],
        )

    return left


def _parse_logical_and(stream: TokenStream) -> ASTNode:
    left = _parse_implies(stream)

    while stream.current() == "and":
        stream.consume()
        right = _parse_implies(stream)
        left = ast.BoolOp(
            op=ast.And(),
            values=[_coerce_expr(left, "and"), _coerce_expr(right, "and")],
        )

    return left


def _parse_implies(stream: TokenStream) -> ASTNode:
    left = _parse_comparison(stream)

    if stream.current() == "implies":
        stream.consume()
        right = _parse_implies(stream)
        return OCLImplies(left, right)

    return left


def _parse_comparison(stream: TokenStream) -> ASTNode:
    left = _parse_range(stream)

    if stream.current() in ("=", "<>", "<=", ">=", "<", ">"):
        op_str = stream.consume()
        right = _parse_range(stream)
        op_map: dict[str, ast.cmpop] = {
            "=": ast.Eq(),
            "<>": ast.NotEq(),
            "<": ast.Lt(),
            "<=": ast.LtE(),
            ">": ast.Gt(),
            ">=": ast.GtE(),
        }
        operator = op_str if isinstance(op_str, str) else "="
        cmpop = op_map[operator]
        return ast.Compare(
            left=_coerce_expr(left, operator),
            ops=[cmpop],
            comparators=[_coerce_expr(right, operator)],
        )

    return left


def _parse_range(stream: TokenStream) -> ASTNode:
    left = _parse_addition(stream)

    if stream.current() == "..":
        stream.consume()
        right = _parse_addition(stream)
        return ast.Call(
            func=ast.Name(id="range", ctx=ast.Load()),
            args=[_coerce_expr(left, ".."), _coerce_expr(right, "..")],
            keywords=[],
        )

    return left


def _parse_addition(stream: TokenStream) -> ASTNode:
    left = _parse_multiplication(stream)

    while stream.current() in ("+", "-"):
        operator = stream.consume()
        right = _parse_multiplication(stream)
        op = ast.Add() if operator == "+" else ast.Sub()
        left = ast.BinOp(
            left=_coerce_expr(left, operator),
            op=op,
            right=_coerce_expr(right, operator),
        )

    return left


def _parse_multiplication(stream: TokenStream) -> ASTNode:
    left = _parse_unary(stream)

    while stream.current() in ("*", "/"):
        operator = stream.consume()
        right = _parse_unary(stream)
        op = ast.Mult() if operator == "*" else ast.Div()
        left = ast.BinOp(
            left=_coerce_expr(left, operator),
            op=op,
            right=_coerce_expr(right, operator),
        )

    return left


def _parse_unary(stream: TokenStream) -> ASTNode:
    if stream.current() == "not":
        stream.consume()
        operand = _parse_unary(stream)
        if isinstance(operand, ast.expr):
            return ast.UnaryOp(op=ast.Not(), operand=operand)
        return operand

    return _parse_primary(stream)


def _parse_navigation_or_attribute(
    stream: TokenStream, expr: ASTNode, operator: str
) -> ASTNode:
    stream.consume()
    prop = stream.consume()
    prop_name = prop if isinstance(prop, str) else ""

    if stream.current() != "(":
        if operator == "." and isinstance(expr, ast.expr):
            return ast.Attribute(value=expr, attr=prop_name, ctx=ast.Load())
        return OCLNavigation(expr, operator, prop_name)

    stream.consume()
    args = _parse_arguments(stream)
    if stream.current() == ")":
        stream.consume()

    if isinstance(expr, ast.expr):
        return ast.Call(
            func=ast.Attribute(value=expr, attr=prop_name, ctx=ast.Load()),
            args=args,  # type: ignore[arg-type]
            keywords=[],
        )

    return OCLNavigation(expr, operator, prop_name)


def _parse_subscript(stream: TokenStream, expr: ASTNode) -> ASTNode:
    stream.consume()
    index = _parse_expression(stream)
    if stream.current() == "]":
        stream.consume()

    return ast.Subscript(
        value=_coerce_expr(expr, "[]"),
        slice=_coerce_expr(index, "[]"),
        ctx=ast.Load(),
    )


def _parse_call(stream: TokenStream, expr: ASTNode) -> ASTNode:
    stream.consume()
    args = _parse_arguments(stream)
    if stream.current() == ")":
        stream.consume()

    return ast.Call(
        func=_coerce_expr(expr, "()"),
        args=[_coerce_expr(arg, "()") for arg in args],
        keywords=[],
    )


def _parse_primary(stream: TokenStream) -> ASTNode:
    match stream.current():
        case "let":
            return _parse_let_in(stream)
        case "if":
            return _parse_if_then_else(stream)
        case "Set" | "Sequence" | "OrderedSet" | "Bag":
            return _parse_collection(stream)
        case "(":
            stream.consume()
            expr = _parse_expression(stream)
            if stream.current() == ")":
                stream.consume()
            return expr

    expr = _parse_atom(stream)

    match stream.current():
        case "->":
            expr = _parse_navigation_or_attribute(stream, expr, "->")
        case ".":
            expr = _parse_navigation_or_attribute(stream, expr, ".")
        case "[":
            expr = _parse_subscript(stream, expr)
        case "(":
            expr = _parse_call(stream, expr)

    return expr


def _parse_atom(stream: TokenStream) -> ASTNode:
    token = stream.current()

    match token:
        case None:
            return ast.Constant(value=None)
        case str() as value if value.startswith("'") and value.endswith("'"):
            stream.consume()
            return ast.Constant(value=value[1:-1].replace("''", "'"))
        case int() | float():
            stream.consume()
            return ast.Constant(value=token)
        case "true" | "false":
            stream.consume()
            return ast.Constant(value=token == "true")
        case "null":
            stream.consume()
            return ast.Constant(value=None)
        case str() as value if value[0].isalpha() or value[0] in "_$":
            stream.consume()
            if "::" in value:
                parts = value.split("::")
                expr: ASTNode = ast.Name(id=parts[0], ctx=ast.Load())
                for part in parts[1:]:
                    expr = ast.Attribute(value=expr, attr=part, ctx=ast.Load())  # type: ignore[arg-type]
                return expr
            return ast.Name(id=value, ctx=ast.Load())
        case _:
            stream.consume()
            return ast.Constant(value=token)


def _parse_arguments(stream: TokenStream) -> list[ASTNode]:
    args: list[ASTNode] = []

    if stream.current() == ")":
        return args

    args.append(_parse_expression(stream))

    while stream.current() == ",":
        stream.consume()
        args.append(_parse_expression(stream))

    return args


def _parse_let_in(stream: TokenStream) -> ASTNode:
    stream.consume()
    var_name = str(stream.consume() or "")
    var_type = None

    if stream.current() == ":":
        stream.consume()
        next_token = stream.consume()
        var_type = str(next_token) if next_token is not None else None

    if stream.current() == "=":
        stream.consume()

    init = _parse_expression(stream)

    if stream.current() == "in":
        stream.consume()

    body = _parse_expression(stream)

    return OCLLetIn(var_name, var_type, init, body)


def _parse_if_then_else(stream: TokenStream) -> ASTNode:
    stream.consume()
    condition = _parse_expression(stream)

    if stream.current() == "then":
        stream.consume()

    then_expr = _parse_expression(stream)

    else_expr = None
    if stream.current() == "else":
        stream.consume()
        else_expr = _parse_expression(stream)

    if stream.current() == "endif":
        stream.consume()

    if (
        isinstance(condition, ast.expr)
        and isinstance(then_expr, ast.expr)
        and (else_expr is None or isinstance(else_expr, ast.expr))
    ):
        return ast.IfExp(
            test=condition,
            body=then_expr,
            orelse=else_expr if else_expr is not None else ast.Constant(value=None),
        )

    return ast.IfExp(
        test=_coerce_expr(condition, "if-then-else"),
        body=_coerce_expr(then_expr, "if-then-else"),
        orelse=(
            _coerce_expr(else_expr, "if-then-else")
            if else_expr is not None
            else ast.Constant(value=None)
        ),
    )


def _parse_collection(stream: TokenStream) -> ASTNode:
    collection_type = str(stream.consume() or "")
    elements: list[ASTNode] = []

    if stream.current() == "{":
        stream.consume()

        if stream.current() != "}":
            elements.append(_parse_expression(stream))
            while stream.current() == ",":
                stream.consume()
                elements.append(_parse_expression(stream))

        if stream.current() == "}":
            stream.consume()

    return OCLCollection(collection_type, elements)


def parse_to_ast(expression: str) -> ASTNode:
    """Parse an OCL expression and build an AST.

    Returns a hierarchical AST combining Python ast nodes (for standard constructs)
    with custom OCL node types (for OCL-specific features like navigation and let-in).

    Args:
        expression: OCL expression string

    Returns:
        AST node (ast node or custom OCL node type)

    Raises:
        ValueError: If expression cannot be parsed
    """
    tokens = tokenize(expression)
    stream = TokenStream(list(tokens))
    return _parse_expression(stream)


def _lower_ast_field(value: object) -> object:
    match value:
        case list() as items:
            return [_lower_ast_field(item) for item in items]
        case tuple() as items:
            return tuple(_lower_ast_field(item) for item in items)
        case ast.AST():
            return _lower_python_ast(value)
        case OCLNavigation() | OCLLetIn() | OCLCollection() | OCLImplies():
            return lower_to_python_ast(value)
        case _:
            return value


def _lower_python_ast(node: ast.AST) -> ast.AST:
    fields = {name: _lower_ast_field(value) for name, value in ast.iter_fields(node)}
    lowered = type(node)(**fields)
    return ast.copy_location(lowered, node)


def lower_to_python_ast(node: ASTNode) -> ast.expr:
    match node:
        case ast.expr():
            lowered = _lower_python_ast(node)
            assert isinstance(lowered, ast.expr)
            return lowered
        case OCLNavigation(target=target, property_name=property_name):
            return ast.Attribute(
                value=lower_to_python_ast(target),
                attr=property_name,
                ctx=ast.Load(),
            )
        case OCLLetIn(variable=variable, init=init, body=body):
            return ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg=variable)],
                        vararg=None,
                        kwonlyargs=[],
                        kw_defaults=[],
                        kwarg=None,
                        defaults=[],
                    ),
                    body=lower_to_python_ast(body),
                ),
                args=[lower_to_python_ast(init)],
                keywords=[],
            )
        case OCLCollection(collection_type="Set", elements=elements):
            return ast.Set(elts=[lower_to_python_ast(element) for element in elements])
        case OCLCollection(elements=elements):
            return ast.List(
                elts=[lower_to_python_ast(element) for element in elements],
                ctx=ast.Load(),
            )
        case OCLImplies(left=left, right=right):
            return ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.UnaryOp(op=ast.Not(), operand=lower_to_python_ast(left)),
                    lower_to_python_ast(right),
                ],
            )
        case _:
            msg = f"Unsupported OCL AST node: {type(node).__name__}"
            raise TypeError(msg)


def unparse(node: ASTNode) -> str:
    return ast.unparse(ast.fix_missing_locations(lower_to_python_ast(node)))


def ocl_to_python(expression: str) -> str:
    """Parse an OCL expression and unparse it as Python source."""

    return unparse(parse_to_ast(expression))


def _split_attribute_path(node: ast.expr) -> list[str] | None:
    match node:
        case ast.Name(id=name):
            return [name]
        case ast.Attribute(value=value, attr=attr):
            if not isinstance(value, ast.expr):
                return None
            if path := _split_attribute_path(value):
                return [*path, attr]
            return None
        case _:
            return None


def _prefixed_path_or_unparse(node: ast.expr) -> str:
    if path := _split_attribute_path(node):
        return f"e.{'.'.join(path)}"
    return ast.unparse(node)


def _if_condition_source(test: ast.expr, body: ast.expr) -> str:
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.NotEq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value is None
        and _split_attribute_path(test.left) == _split_attribute_path(body)
    ):
        return _prefixed_path_or_unparse(body)

    return _prefixed_path_or_unparse(test)


def _not_empty_source_path(test: ast.expr) -> list[str] | None:
    if (
        isinstance(test, ast.Call)
        and isinstance(test.func, ast.Attribute)
        and test.func.attr == "notEmpty"
        and not test.args
    ):
        return _split_attribute_path(test.func.value)
    return None


def _prefixed_list_or_unparse(node: ast.expr) -> str:
    if isinstance(node, ast.List):
        elements = ", ".join(_prefixed_path_or_unparse(elt) for elt in node.elts)
        return f"[{elements}]"
    return ast.unparse(node)


def _iter_class_hierarchy(cls: UML.Class) -> Iterator[UML.Class]:
    yield cls

    for generalization in cls.generalization:
        general = generalization.general
        if isinstance(general, UML.Class):
            yield general


def _all_attributes_in_hierarchy(owning_class: UML.Class) -> Iterator[UML.Property]:
    for cls in _iter_class_hierarchy(owning_class):
        yield from cls.ownedAttribute


def _head_is_multi_valued(path: list[str], owning_class: UML.Class) -> bool:
    if not path:
        return False

    head = path[0]
    for attribute in _all_attributes_in_hierarchy(owning_class):
        if attribute.name == head:
            return UML.recipes.get_multiplicity_upper_value(attribute) != 1

    return False


# TODO: should also return a set of involved UML.Property's, so we can add notifications
def ocl_derive_to_python(expression: str, owning_class: UML.Class) -> str:
    node = lower_to_python_ast(parse_to_ast(expression))

    target = node
    if (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Eq)
        and len(node.comparators) == 1
    ):
        target = node.comparators[0]

    if isinstance(target, ast.IfExp):
        if source_path := _not_empty_source_path(target.test):
            body_path = _split_attribute_path(target.body)
            if body_path and body_path[: len(source_path)] == source_path:
                source = f"e.{'.'.join(source_path)}"
                taill = body_path[len(source_path) :]
                projection = f".{'.'.join(taill)}" if taill else ""
                body = f"{source}[:]{projection}"
                orelse = _prefixed_list_or_unparse(target.orelse)
                return f"lambda e: {body} if {source} else {orelse}"

        body = _prefixed_path_or_unparse(target.body)
        condition = _if_condition_source(target.test, target.body)
        orelse = _prefixed_list_or_unparse(target.orelse)
        return f"{body} if {condition} else {orelse}"

    if (
        isinstance(target, ast.Call)
        and isinstance(target.func, ast.Attribute)
        and target.func.attr == "selectByKind"
        and len(target.args) == 1
        and isinstance(target.args[0], ast.Name)
    ):
        source_path = _split_attribute_path(target.func.value)
        if source_path:
            if len(source_path) > 1 and _head_is_multi_valued(
                source_path, owning_class
            ):
                source = f"e.{source_path[0]}[:].{'.'.join(source_path[1:])}"
            else:
                source = f"e.{'.'.join(source_path)}"
            return (
                f"lambda e: [x for x in {source} if isinstance(x, {target.args[0].id})]"
            )

    if path := _split_attribute_path(target):
        if len(path) > 1 and _head_is_multi_valued(path, owning_class):
            head = f"e.{path[0]}"
            tail = ".".join(path[1:])
            return f"lambda e: [*{head}[:].{tail}] or []"
        full = f"e.{'.'.join(path)}"
        guard = f"e.{path[0]}"
        return f"lambda e: {guard} and [{full}] or [None]"

    return ""
