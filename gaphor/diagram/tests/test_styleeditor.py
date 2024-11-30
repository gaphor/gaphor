import pytest
from gi.repository import Gdk

from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.diagram.general import Line
from gaphor.diagram.styleeditor import (
    StyleEditor,
    StylePropertyPage,
    from_gdk_rgba,
    to_gdk_rgba,
)
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes import ClassItem


@pytest.fixture
def style_sheet(element_factory):
    assert not next(element_factory.select(StyleSheet), None)
    return element_factory.create(StyleSheet)


@pytest.fixture
def style_editor(create, style_sheet, event_manager):
    item = create(ClassItem, UML.Class)
    style_editor = StyleEditor(item, style_sheet, event_manager, None, lambda: None)
    style_editor.present()
    yield style_editor
    style_editor.close()


class MockMainWindow:
    @property
    def window(self):
        return None


def test_style_editor_page(diagram, event_manager, element_factory):
    item = diagram.create(Line)
    property_page = StylePropertyPage(
        item, event_manager, element_factory, MockMainWindow()
    )
    widget = property_page.construct()
    assert widget
    style_editor = find(widget, "style-editor")
    assert style_editor


def test_style_editor_creation(style_editor):
    color_picker = find(style_editor.window, "color")
    border_radius = find(style_editor.window, "border-radius")
    background_color = find(style_editor.window, "background-color")
    text_color = find(style_editor.window, "text-color")

    assert color_picker
    assert border_radius
    assert background_color
    assert text_color


def test_color_from_style_sheet(style_editor, style_sheet: StyleSheet):
    color_picker = find(style_editor.window, "color")
    border_radius = find(style_editor.window, "border-radius")
    background_color = find(style_editor.window, "background-color")
    text_color = find(style_editor.window, "text-color")

    assert border_radius.get_value() == 0.0
    assert from_gdk_rgba(color_picker.get_rgba()) == "rgba(0, 0, 0, 1.0)"
    assert from_gdk_rgba(background_color.get_rgba()) == "rgba(0, 0, 0, 0.0)"
    assert from_gdk_rgba(text_color.get_rgba()) == "rgba(0, 0, 0, 1.0)"


def test_set_border_radius(style_editor, style_sheet):
    border_radius = find(style_editor.window, "border-radius")
    border_radius.set_value(10)

    assert "border-radius: 10.0" in style_sheet.instant_style_declarations


def test_set_color(style_editor, style_sheet: StyleSheet):
    color_picker = find(style_editor.window, "color")
    color_picker.set_rgba(to_gdk_rgba("rgba(255, 0, 0, 1)"))
    style_editor.on_color_set(color_picker)

    assert "color: rgba(255, 0, 0, 1.0)" in style_sheet.instant_style_declarations


def test_set_background_color(style_editor, style_sheet):
    background_color = find(style_editor.window, "background-color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 255, 0, 1)")
    background_color.set_rgba(rgba)
    style_editor.on_background_color_set(background_color)

    assert (
        "background-color: rgba(0, 255, 0, 1.0)"
        in style_sheet.instant_style_declarations
    )


def test_set_text_color(style_editor, style_sheet):
    text_color = find(style_editor.window, "text-color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 255, 1)")
    text_color.set_rgba(rgba)
    style_editor.on_text_color_set(text_color)

    assert "text-color: rgba(0, 0, 255, 1.0)" in style_sheet.instant_style_declarations


def test_change_name(style_editor, style_sheet):
    item = style_editor.subject
    item.subject.name = "Name"
    color = find(style_editor.window, "color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 255, 1)")
    color.set_rgba(rgba)
    style_editor.on_color_set(color)
    assert (
        'class[name="Name"] {\n  color: rgba(0, 0, 255, 1.0)'
        in style_sheet.instant_style_declarations
    )

    item.subject.name = "New Name"

    assert (
        'class[name="New Name"] {\n  color: rgba(0, 0, 255, 1.0)'
        in style_sheet.instant_style_declarations
    )


def test_element_deleted(style_editor, style_sheet):
    item = style_editor.subject
    item.subject.name = "Name"
    color = find(style_editor.window, "color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 255, 1)")
    color.set_rgba(rgba)
    style_editor.on_color_set(color)
    assert (
        'class[name="Name"] {\n  color: rgba(0, 0, 255, 1.0)'
        in style_sheet.instant_style_declarations
    )

    item.unlink()

    assert style_sheet.instant_style_declarations == ""


def test_export(style_sheet, style_editor, diagram, element_factory, event_manager):
    item = style_editor.subject
    item.subject.name = "Name"

    color = find(style_editor.window, "color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 255, 1)")
    color.set_rgba(rgba)
    style_editor.on_color_set(color)

    export = find(style_editor.window, "export")
    style_editor.on_export(export)

    assert "rgba(0, 0, 255, 1.0)" in style_sheet.styleSheet
