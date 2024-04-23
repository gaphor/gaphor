import pytest

from gaphor.core.styling import compile_style_sheet
from gaphor.core.styling.selectors import SelectorError


class Node:
    def __init__(
        self,
        name,
        parent=None,
        children=None,
        attributes=None,
        state=(),
        pseudo=None,
        dark_mode=None,
    ):
        if attributes is None:
            attributes = {}
        self._name = name
        self._parent = parent
        self._children = children or []
        self._attributes = attributes
        self._state = state
        self.pseudo = pseudo
        self.dark_mode = dark_mode

        if parent:
            parent._children.append(self)  # noqa: SLF001
        for c in self._children:
            c._parent = self  # noqa: SLF001

    def name(self):
        return self._name

    def parent(self):
        return self._parent

    def children(self):
        return iter(self._children)

    def attribute(self, name):
        return self._attributes.get(name, "") if name in self._attributes else None

    def state(self):
        return self._state


def test_node_test_object_parent_child():
    c = Node("child")
    p = Node("parent", children=[c])

    assert c.name() == "child"
    assert p.name() == "parent"
    assert c.parent() is p
    assert c in p.children()


def test_node_test_object_child_parent():
    p = Node("parent")
    c = Node("child", parent=p)

    assert c.name() == "child"
    assert p.name() == "parent"
    assert c.parent() is p
    assert c in p.children()


def test_select_all():
    css = "* {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector("any")


def test_select_name():
    css = "classitem {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem"))
    assert not selector(Node("packageitem"))


def test_select_inside_combinator():
    css = "classitem nested {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("nested", parent=Node("classitem")))
    assert selector(
        Node(
            "nested",
            parent=Node("other", parent=Node("classitem")),
        )
    )
    assert not selector(Node("nested"))
    assert not selector(Node("classitem"))


def test_select_parent_combinator():
    css = "classitem > nested {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("nested", parent=Node("classitem")))
    assert not selector(
        Node(
            "nested",
            parent=Node("other", parent=Node("classitem")),
        )
    )
    assert not selector(Node("nested"))
    assert not selector(Node("classitem"))


def test_select_sibling_combinator():
    css = "previous + sibling {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("sibling", parent=Node("parent", children=[Node("previous")])))
    assert not selector(
        Node("sibling", parent=Node("parent", children=[Node("other")]))
    )
    assert not selector(
        Node("other", parent=Node("parent", children=[Node("previous")]))
    )
    assert not selector(Node("sibling"))


def test_attributes():
    css = "classitem[subject] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "val"}))
    assert not selector(Node("classitem"))


def test_attribute_equal():
    css = "classitem[subject=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert not selector(Node("classitem", attributes={"subject": "bar"}))
    assert not selector(Node("classitem"))


def test_attribute_in_list():
    css = "classitem[subject~=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foo bar"}))
    assert not selector(Node("classitem", attributes={"subject": "bar"}))
    assert not selector(Node("classitem"))


def test_attribute_starts_with():
    css = "classitem[subject^=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foomania"}))
    assert not selector(Node("classitem", attributes={"subject": "not foo"}))
    assert not selector(Node("classitem"))


def test_attribute_starts_with_dash():
    css = "classitem[subject|=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foo-mania"}))
    assert not selector(Node("classitem", attributes={"subject": "foomania"}))
    assert not selector(Node("classitem"))


def test_attribute_ends_with():
    css = "classitem[subject$=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "manicfoo"}))
    assert not selector(Node("classitem", attributes={"subject": "fooless"}))
    assert not selector(Node("classitem"))


def test_attribute_contains():
    css = "classitem[subject*=foo] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "be foo-ish"}))
    assert not selector(Node("classitem", attributes={"subject": "fobic"}))
    assert not selector(Node("classitem"))


def test_attributes_with_dots():
    css = "classitem[subject.members] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject.members": "foo"}))


def test_attributes_are_lower_case():
    css = "ClassItem[MixedCase] {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", attributes={"mixedcase": "foo"}))


def test_empty_pseudo_selector():
    css = ":empty {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("node"))
    assert not selector(Node("node", children=[Node("child")]))


def test_empty_pseudo_selector_with_name():
    css = "node:empty {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("node"))
    assert not selector(Node("node", children=[Node("child")]))


def test_root_pseudo_selector_with_name():
    css = ":root {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("node"))
    assert not selector(Node("node", parent=Node("child")))


def test_first_child_selector():
    css = "node:first-child {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert not selector(Node("node", parent=Node("parent", children=[Node("node")])))
    assert selector(Node("node", parent=Node("parent")))
    assert not selector(Node("sibling"))


@pytest.mark.parametrize(
    "state",
    ["hover", "focus", "active", "drop", "disabled"],
)
def test_hovered_pseudo_selector(state):
    css = f":{state} {{}}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("node", state=(state,)))
    assert selector(Node("node", state=(state, "other-state")))
    assert not selector(Node("node", state=()))


def test_is_pseudo_selector():
    css = "classitem:is(:hover, :active) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", state=("hover",)))
    assert selector(Node("classitem", state=("active",)))
    assert selector(Node("classitem", state=("hover", "active")))
    assert not selector(Node("classitem"))


def test_not_pseudo_selector():
    css = "classitem:not(:hover) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem"))
    assert selector(Node("classitem", state=("active")))
    assert not selector(Node("classitem", state=("hover",)))
    assert not selector(Node("classitem", state=("hover", "active")))


def test_has_pseudo_selector():
    css = "classitem:has(nested) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", children=[Node("nested")]))
    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert not selector(Node("classitem"))


def test_has_pseudo_selector_with_wildcard():
    css = "classitem:has(*) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("classitem", children=[Node("nested")]))
    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert not selector(Node("classitem"))


def test_has_pseudo_selector_with_nested_selector():
    css = "classitem:has(middle nested) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert not selector(Node("classitem", children=[Node("nested")]))
    assert selector(
        Node(
            "classitem",
            children=[
                Node("middle", children=[Node("other", children=[Node("nested")])])
            ],
        )
    )


def test_has_pseudo_selector_with_complex_selector():
    css = "classitem:has(middle > nested) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert not selector(Node("classitem", children=[Node("nested")]))
    assert not selector(
        Node(
            "classitem",
            children=[
                Node("middle", children=[Node("other", children=[Node("nested")])])
            ],
        )
    )


# TODO: customize parser to allow expressions like ":has(> nested)"
def test_has_pseudo_selector_with_combinator_is_not_supported():
    # NB. This is according to the CSS spec, but our parser is not
    # able to deal with this. This test is just here to illustrate.
    css = "classitem:has(> nested) {}"

    error, payload = next(compile_style_sheet(css))

    assert error == "error"


def test_parse_empty_pseudo_element():
    css = "node::after {}"

    selector, declarations = next(compile_style_sheet(css))

    assert declarations == {}
    assert not selector(Node("node"))
    assert selector(Node("node", pseudo="after"))


def test_has_and_is_selector():
    css = "node:has(:is(:hover)) {}"

    selector, _declarations = next(compile_style_sheet(css))

    assert selector(
        Node(
            "node",
            children=[Node("foo", children=[Node("bar", state=("hover",))])],
        )
    )


@pytest.mark.parametrize(
    "css",
    [
        "@media(prefers-color-scheme = dark) { node { color: blue; } }",
        "@media prefers-color-scheme = dark { node { color: blue; } }",
        "@media(dark-mode) { node { color: blue; } }",
        "@media dark-mode { node { color: blue; } }",
    ],
)
def test_media_query(css):
    selector, _declarations = next(compile_style_sheet(css))

    assert selector(Node("node", dark_mode=True))


@pytest.mark.parametrize(
    "css,exc_type",
    [
        ["@media(prefers-color-scheme { * { color: blue; } }", StopIteration],
        ["@media prefers-color-scheme true) { * { color: blue; } }", SelectorError],
        ["@media((other-query = = dark) { * { color: blue; } }", StopIteration],
        ["@media{(prefers-color-scheme = dark) { color }", StopIteration],
    ],
)
def test_invalid_media_query(css, exc_type):
    with pytest.raises(exc_type):
        next(compile_style_sheet(css))
