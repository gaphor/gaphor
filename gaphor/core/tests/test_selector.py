from gaphor.core.styling import parse_style_sheet


class Node:
    def __init__(self, local_name, parent=None, children=None, attributes={}):
        self._local_name = local_name
        self._parent = parent
        self._children = children or []
        self._attributes = attributes

        if parent:
            parent._children.append(self)
        for c in self._children:
            c._parent = self

    def local_name(self):
        return self._local_name

    def parent(self):
        return self._parent

    def children(self):
        yield from self._children

    def attribute(self, name):
        return self._attributes.get(name, "")


def test_node_test_object_parent_child():
    c = Node("child")
    p = Node("parent", children=[c])

    assert c.local_name() == "child"
    assert p.local_name() == "parent"
    assert c.parent() is p
    assert c in p.children()


def test_node_test_object_child_parent():
    p = Node("parent")
    c = Node("child", parent=p)

    assert c.local_name() == "child"
    assert p.local_name() == "parent"
    assert c.parent() is p
    assert c in p.children()


def test_select_all():
    css = "* {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    print(selector)
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
    assert selector(Node("nested", parent=Node("other", parent=Node("classitem")),))
    assert not selector(Node("nested"))
    assert not selector(Node("classitem"))


def test_select_parent_combinator():
    css = "classitem > nested {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("nested", parent=Node("classitem")))
    assert not selector(Node("nested", parent=Node("other", parent=Node("classitem")),))
    assert not selector(Node("nested"))
    assert not selector(Node("classitem"))


def test_has_selector():
    css = "classitem:has(nested) {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(Node("classitem", children=[Node("nested")]))
    assert selector(
        Node("classitem", children=[Node("middle", children=[Node("nested")])],)
    )
    assert not selector(Node("classitem"))
