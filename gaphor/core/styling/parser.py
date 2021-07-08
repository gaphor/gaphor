"""Parser for CSS selectors, based on the tinycss2 tokenizer.

Original module: cssselect2.parser
:copyright: (c) 2012 by Simon Sapin, 2017 by Guillaume Ayoub.
:license: BSD, see LICENSE for more details.
"""

from tinycss2 import parse_component_value_list

__all__ = ["parse"]


def parse(input, namespaces=None):
    """Yield tinycss2 selectors found in given ``input``.

    :param input:
        A string, or an iterable of tinycss2 component values.
    """
    if isinstance(input, str):
        input = parse_component_value_list(input)
    tokens = TokenStream(input)
    namespaces = namespaces or {}
    yield parse_selector(tokens, namespaces)
    tokens.skip_whitespace_and_comment()
    while 1:
        next = tokens.next()
        if next is None:
            return
        elif next == ",":
            yield parse_selector(tokens, namespaces)
        else:
            raise SelectorError(next, "unpexpected %s token." % next.type)


def parse_selector(tokens, namespaces):
    result = parse_compound_selector(tokens, namespaces)
    while 1:
        has_whitespace = tokens.skip_whitespace()
        while tokens.skip_comment():
            has_whitespace = tokens.skip_whitespace() or has_whitespace
        peek = tokens.peek()
        if peek in (">", "+", "~"):
            combinator = peek.value
            tokens.next()
        elif peek is None or peek == "," or not has_whitespace:
            return result
        else:
            combinator = " "
        compound = parse_compound_selector(tokens, namespaces)
        result = CombinedSelector(result, combinator, compound)


def parse_compound_selector(tokens, namespaces):
    type_selectors = parse_type_selector(tokens, namespaces)
    simple_selectors = type_selectors if type_selectors is not None else []
    while 1:
        simple_selector = parse_simple_selector(tokens, namespaces)
        if simple_selector is None:
            break
        simple_selectors.append(simple_selector)

    if simple_selectors or type_selectors is not None:
        return CompoundSelector(simple_selectors)
    peek = tokens.peek()
    raise SelectorError(
        peek,
        "expected a compound selector, got %s" % (peek.type if peek else "EOF"),
    )


def parse_type_selector(tokens, namespaces):
    tokens.skip_whitespace()
    qualified_name = parse_qualified_name(tokens, namespaces)
    if qualified_name is None:
        return None

    simple_selectors = []
    namespace, local_name = qualified_name
    if local_name is not None:
        simple_selectors.append(LocalNameSelector(local_name))
    if namespace is not None:
        simple_selectors.append(NamespaceSelector(namespace))  # type: ignore[arg-type]
    return simple_selectors


def parse_simple_selector(tokens, namespaces):
    peek = tokens.peek()
    if peek is None:
        return None
    if peek.type == "hash" and peek.is_identifier:
        tokens.next()
        return IDSelector(peek.value)
    elif peek == ".":
        tokens.next()
        next = tokens.next()
        if next is None or next.type != "ident":
            raise SelectorError(next, "Expected a class name, got %s" % next)
        return ClassSelector(next.value)
    elif peek.type == "[] block":
        tokens.next()
        return parse_attribute_selector(TokenStream(peek.content), namespaces)
    elif peek == ":":
        tokens.next()
        next = tokens.next()
        if next == ":":
            next = tokens.next()
            if next is None or next.type != "ident":
                raise SelectorError(
                    next, "Expected a pseudo-element name, got %s" % next
                )
            return PseudoElementSelector(next.lower_value)
        elif next is not None and next.type == "ident":
            return PseudoClassSelector(next.lower_value)
        elif next is not None and next.type == "function":
            return FunctionalPseudoClassSelector(next.lower_name, next.arguments)
        else:
            raise SelectorError(next, "unexpected %s token." % next)
    else:
        return None


def parse_attribute_selector(tokens, namespaces):
    tokens.skip_whitespace()
    qualified_name = parse_qualified_name(tokens, namespaces, is_attribute=True)
    if qualified_name is None:
        next = tokens.next()
        raise SelectorError(next, "expected attribute name, got %s" % next)
    namespace, local_name = qualified_name

    # Allow syntax like "subject.ownedAttribute"
    if local_name:
        name, lower_name = local_name
        while 1:
            peek = tokens.peek()
            if peek == ".":
                next = tokens.next()
                name += next.value
                lower_name += next.value
            elif peek and peek.type == "ident":
                next = tokens.next()
                name += next.value
                lower_name += next.lower_value
            else:
                break

        local_name = name, lower_name

    tokens.skip_whitespace()
    peek = tokens.peek()
    if peek is None:
        operator = None
        value = None
    elif peek in ("=", "~=", "|=", "^=", "$=", "*="):
        operator = peek.value
        tokens.next()
        tokens.skip_whitespace()
        next = tokens.next()
        if next is None or next.type not in ("ident", "string"):
            next_type = "None" if next is None else next.type
            raise SelectorError(next, "expected attribute value, got %s" % next_type)
        value = next.value
    else:
        raise SelectorError(peek, "expected attribute selector operator, got %s" % peek)

    tokens.skip_whitespace()
    next = tokens.next()
    if next is not None:
        raise SelectorError(next, "expected ], got %s" % next.type)
    return AttributeSelector(namespace, local_name, operator, value)


def parse_qualified_name(tokens, namespaces, is_attribute=False):
    """Return ``(namespace, local)`` for given tokens.

    Can also return ``None`` for a wildcard.

    The empty string for ``namespace`` means "no namespace".
    """
    peek = tokens.peek()
    if peek is None:
        return None
    if peek.type == "ident":
        first_ident = tokens.next()
        peek = tokens.peek()
        if peek != "|":
            namespace = "" if is_attribute else namespaces.get(None, None)
            return namespace, (first_ident.value, first_ident.lower_value)
        tokens.next()
        namespace = namespaces.get(first_ident.value)
        if namespace is None:
            raise SelectorError(
                first_ident, "undefined namespace prefix: " + first_ident.value
            )
    elif peek == "*":
        next = tokens.next()
        peek = tokens.peek()
        if peek != "|":
            if is_attribute:
                raise SelectorError(next, "Expected local name, got %s" % next.type)
            return namespaces.get(None, None), None
        tokens.next()
        namespace = None
    elif peek == "|":
        tokens.next()
        namespace = ""
    else:
        return None

    # If we get here, we just consumed '|' and set ``namespace``
    next = tokens.next()
    if next.type == "ident":
        return namespace, (next.value, next.lower_value)
    elif next == "*" and not is_attribute:
        return namespace, None
    else:
        raise SelectorError(next, "Expected local name, got %s" % next.type)


class SelectorError(ValueError):
    """A specialized ``ValueError`` for invalid selectors."""


class TokenStream(object):
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.peeked = []  # In reversed order

    def next(self):
        if self.peeked:
            return self.peeked.pop()
        else:
            return next(self.tokens, None)

    def peek(self):
        if not self.peeked:
            self.peeked.append(next(self.tokens, None))
        return self.peeked[-1]

    def skip(self, skip_types):
        found = False
        while 1:
            peek = self.peek()
            if peek is None or peek.type not in skip_types:
                break
            self.next()
            found = True
        return found

    def skip_whitespace(self):
        return self.skip(["whitespace"])

    def skip_comment(self):
        return self.skip(["comment"])

    def skip_whitespace_and_comment(self):
        return self.skip(["comment", "whitespace"])


class CombinedSelector(object):
    def __init__(self, left, combinator, right):
        #: Combined or compound selector
        self.left = left
        # One of `` `` (a single space), ``>``, ``+`` or ``~``.
        self.combinator = combinator
        #: compound selector
        self.right = right

    @property
    def specificity(self):
        a1, b1, c1 = self.left.specificity
        a2, b2, c2 = self.right.specificity
        return a1 + a2, b1 + b2, c1 + c2

    def __repr__(self):
        return "{!r}{}{!r}".format(self.left, self.combinator, self.right)


class CompoundSelector(object):
    """Aka.

    sequence of simple selectors, in Level 3.
    """

    def __init__(self, simple_selectors):
        self.simple_selectors = simple_selectors

    @property
    def specificity(self):
        if self.simple_selectors:
            return tuple(
                map(sum, zip(*(sel.specificity for sel in self.simple_selectors)))
            )
        else:
            return 0, 0, 0

    def __repr__(self):
        return "".join(map(repr, self.simple_selectors))


class LocalNameSelector(object):
    specificity = 0, 0, 1

    def __init__(self, local_name):
        self.local_name, self.lower_local_name = local_name

    def __repr__(self):
        return self.local_name


class NamespaceSelector(object):
    specificity = 0, 0, 0

    def __init__(self, namespace):
        #: The namespace URL as a string,
        #: or the empty string for elements not in any namespace.
        self.namespace = namespace

    def __repr__(self):
        if self.namespace == "":
            return "|"
        else:
            return "{%s}|" % self.namespace


class IDSelector(object):
    specificity = 1, 0, 0

    def __init__(self, ident):
        self.ident = ident

    def __repr__(self):
        return "#" + self.ident


class ClassSelector(object):
    specificity = 0, 1, 0

    def __init__(self, class_name):
        self.class_name = class_name

    def __repr__(self):
        return "." + self.class_name


class AttributeSelector(object):
    specificity = 0, 1, 0

    def __init__(self, namespace, name, operator, value):
        self.namespace = namespace
        self.name, self.lower_name = name
        #: A string like ``=`` or ``~=``, or None for ``[attr]`` selectors
        self.operator = operator
        #: A string, or None for ``[attr]`` selectors
        self.value = value

    def __repr__(self):
        namespace = "*|" if self.namespace is None else "{%s}" % self.namespace
        return "[{}{}{}{!r}]".format(namespace, self.name, self.operator, self.value)


class PseudoClassSelector:
    specificity = 0, 1, 0

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return ":" + self.name


class PseudoElementSelector:
    specificity = 0, 0, 1

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "::" + self.name


class FunctionalPseudoClassSelector(object):
    specificity = 0, 1, 0

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return ":{}{!r}".format(self.name, tuple(self.arguments))
