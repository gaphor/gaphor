from gaphor.diagram.uibuilder import translated_ui_string


def test_ui_builder_builds_from_resources():
    ui_xml = translated_ui_string("gaphor.diagram", "propertypages.glade")

    assert "translatable=" not in ui_xml
