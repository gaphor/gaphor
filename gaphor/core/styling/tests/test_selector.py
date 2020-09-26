import pytest

from gaphor.core.styling import parse_style_sheet


class Node:
    def __init__(self, name, parent=None, children=None, attributes={}, state=()):
        self._name = name
        self._parent = parent
        self._children = children or []
        self._attributes = attributes
        self._state = state

        if parent:
            parent._children.append(self)
        for c in self._children:
            c._parent = self

    def name(self):
        return self._name

    def parent(self):
        return self._parent

    def children(self):
        return iter(self._children)

    def attribute(self, name):
        return self._attributes.get(name, "")

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

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector("any")


def test_select_name():
    css = "classitem {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem"))
    assert not selector(Node("packageitem"))


def test_select_inside_combinator():
    css = "classitem nested {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

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

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("nested", parent=Node("classitem")))
    assert not selector(
        Node(
            "nested",
            parent=Node("other", parent=Node("classitem")),
        )
    )
    assert not selector(Node("nested"))
    assert not selector(Node("classitem"))


def test_attributes():
    css = "classitem[subject] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "val"}))
    assert not selector(Node("classitem"))
    assert not selector(Node("classitem", attributes={"subject": None}))


def test_attribute_equal():
    css = "classitem[subject=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert not selector(Node("classitem", attributes={"subject": "bar"}))


def test_attribute_in_list():
    css = "classitem[subject~=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foo bar"}))
    assert not selector(Node("classitem", attributes={"subject": "bar"}))


def test_attribute_starts_with():
    css = "classitem[subject^=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foomania"}))
    assert not selector(Node("classitem", attributes={"subject": "not foo"}))


def test_attribute_starts_with_dash():
    css = "classitem[subject|=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "foo-mania"}))
    assert not selector(Node("classitem", attributes={"subject": "foomania"}))


def test_attribute_ends_with():
    css = "classitem[subject$=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "manicfoo"}))
    assert not selector(Node("classitem", attributes={"subject": "fooless"}))


def test_attribute_contains():
    css = "classitem[subject*=foo] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject": "foo"}))
    assert selector(Node("classitem", attributes={"subject": "be foo-ish"}))
    assert not selector(Node("classitem", attributes={"subject": "fobic"}))


def test_attributes_with_dots():
    css = "classitem[subject.members] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"subject.members": "foo"}))


def test_attributes_are_lower_case():
    css = "ClassItem[MixedCase] {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", attributes={"mixedcase": "foo"}))


def test_empty_pseudo_selector():
    css = ":empty {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("node"))
    assert specificity == (0, 1, 0)
    assert not selector(Node("node", children=[Node("child")]))


def test_empty_pseudo_selector_with_name():
    css = "node:empty {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("node"))
    assert not selector(Node("node", children=[Node("child")]))
    assert specificity == (0, 1, 1)


@pytest.mark.parametrize(
    "state",
    ["root", "hover", "focus", "active", "drop"],
)
def test_hovered_pseudo_selector(state):

    css = f":{state} {{}}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("node", state=(state,)))
    assert selector(Node("node", state=(state, "other-state")))
    assert not selector(Node("node", state=()))


def test_is_pseudo_selector():
    css = "classitem:is(:hover, :active) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", state=("hover",)))
    assert selector(Node("classitem", state=("active",)))
    assert selector(Node("classitem", state=("hover", "active")))
    assert specificity == (0, 1, 1)
    assert not selector(Node("classitem"))


def test_not_pseudo_selector():
    css = "classitem:not(:hover) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem"))
    assert selector(Node("classitem", state=("active")))
    assert specificity == (0, 1, 1)
    assert not selector(Node("classitem", state=("hover",)))
    assert not selector(Node("classitem", state=("hover", "active")))


def test_has_pseudo_selector():
    css = "classitem:has(nested) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", children=[Node("nested")]))
    assert specificity == (0, 0, 2)
    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert not selector(Node("classitem"))


def test_has_pseudo_selector_with_complex_selector():
    css = "classitem:has(middle > nested) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])])
    )
    assert specificity == (0, 0, 3)
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

    error, payload = next(parse_style_sheet(css))

    assert error == "error"


def test_has_and_is_selector():
    css = "node:has(:is(:hover)) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(
        Node(
            "node",
            children=[Node("foo", children=[Node("bar", state=("hover",))])],
        )
    )
