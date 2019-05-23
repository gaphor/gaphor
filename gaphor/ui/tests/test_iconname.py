import pytest

from gaphor.ui.iconname import to_kebab_case


def test_kebab_case():
    assert to_kebab_case("Class") == "class"
    assert to_kebab_case("FooBar") == "foo-bar"
    assert to_kebab_case("FooBarBaz") == "foo-bar-baz"
