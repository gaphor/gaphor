from gaphor.i18n import translated_ui_string


def test_ui_builder_builds_from_resources():
    ui_xml = translated_ui_string("gaphor.diagram", "propertypages.ui")

    assert "translatable=" not in ui_xml
