import pytest

from gaphor.ui.help import new_builder


@pytest.fixture(autouse=True)
def builder():
    return new_builder("preferences")


def test_preferences_dark_mode(builder):
    style_variant = builder.get_object("style_variant")
    assert style_variant.get_selected() == 0


def test_preferences_use_english(builder):
    use_english = builder.get_object("use_english")
    assert use_english.get_active() == 0
