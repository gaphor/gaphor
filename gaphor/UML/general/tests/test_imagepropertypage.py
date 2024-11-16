from pathlib import Path

from gaphor.diagram.tests.fixtures import find
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.general.image import ImageItem
from gaphor.UML.general.imagepropertypage import (
    ImagePropertyPage,
)


def test_picture_property_select_opens_dialog(monkeypatch, diagram, event_manager):
    # Init objects
    picture = diagram.create(ImageItem)
    property_page = ImagePropertyPage(picture, event_manager)
    widget = property_page.construct()

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr("gaphor.UML.general.imagepropertypage.open_file_dialog", call)

    # Emulate the button click event
    button_widget = find(widget, "select-picture-button")
    button_widget.set_activate_signal_from_name("clicked")

    # Test code
    button_widget.activate()

    assert called is True


def test_picture_property_select_valid_name(monkeypatch, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-image"
    ).item_factory(diagram)
    property_page = ImagePropertyPage(picture, event_manager)

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr("gaphor.UML.general.imagepropertypage.error_handler", call)
    # Test code
    temp_image = Path("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert called is False
    assert picture.subject.name == "gaphor-24x24"


def test_picture_property_select_keep_name(monkeypatch, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-image"
    ).item_factory(diagram)
    property_page = ImagePropertyPage(picture, event_manager)

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr("gaphor.UML.general.imagepropertypage.error_handler", call)

    # Test code
    picture.subject.name = "old_name"
    temp_image = Path("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert called is False
    assert picture.subject.name == "old_name"


def test_picture_property_select_replace_name_chars(diagram, event_manager):
    # Init objects
    property_page = ImagePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/UML/general/tests/test.+gaphor$48-48.png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "test__gaphor_48-48"


def test_picture_property_select_empty_name(diagram, event_manager):
    # Init objects
    property_page = ImagePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/UML/general/tests/.png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "_png"


def test_picture_property_select_empty_extension(diagram, event_manager):
    # Init objects
    property_page = ImagePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/UML/general/tests/test_png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "test_png"
