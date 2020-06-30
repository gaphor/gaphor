from gaphor.core.styling import parse_style_sheet


class SelectorProperties:
    def __init__(self, local_name, parent=None):
        self._local_name = local_name
        self._parent = parent

    def local_name(self):
        return self._local_name

    def parent(self):
        return self._parent

    def ancestors(self):
        parent = self._parent
        if parent:
            yield parent
            yield from parent.ancestors()


def test_select_all():
    css = "* {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    print(selector)
    assert selector("any")


def test_select_name():
    css = "classitem {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(SelectorProperties("classitem"))
    assert not selector(SelectorProperties("packageitem"))


def test_select_inside_combinator():
    css = "classitem nested {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(
        SelectorProperties("nested", parent=SelectorProperties("classitem"))
    )
    assert selector(
        SelectorProperties(
            "nested",
            parent=SelectorProperties("other", parent=SelectorProperties("classitem")),
        )
    )
    assert not selector(SelectorProperties("nested"))
    assert not selector(SelectorProperties("classitem"))


def test_select_parent_combinator():
    css = "classitem > nested {}"

    (selector, specificity), payload = next(parse_style_sheet(css))

    assert selector(
        SelectorProperties("nested", parent=SelectorProperties("classitem"))
    )
    assert not selector(
        SelectorProperties(
            "nested",
            parent=SelectorProperties("other", parent=SelectorProperties("classitem")),
        )
    )
    assert not selector(SelectorProperties("nested"))
    assert not selector(SelectorProperties("classitem"))
