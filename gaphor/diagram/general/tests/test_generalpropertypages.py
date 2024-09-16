from pathlib import Path

from gaphor.core.modeling import Comment
from gaphor.diagram.diagramtoolbox import general_tools
from gaphor.diagram.general import MetadataItem
from gaphor.diagram.general.generalpropertypages import (
    CommentPropertyPage,
    MetadataPropertyPage,
    PicturePropertyPage,
)
from gaphor.diagram.general.picture import PictureItem
from gaphor.diagram.tests.fixtures import find


def test_comment_property_page_body(element_factory, event_manager):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject, event_manager)

    widget = property_page.construct()
    comment = find(widget, "comment")
    comment.get_buffer().set_text("test")

    assert subject.body == "test"


def test_comment_property_page_update_text(element_factory, event_manager):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject, event_manager)

    widget = property_page.construct()
    comment = find(widget, "comment")
    subject.body = "test"
    buffer = comment.get_buffer()

    assert (
        buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) == "test"
    )


def test_metadata_property_page(diagram, event_manager):
    metadata = diagram.create(MetadataItem)

    property_page = MetadataPropertyPage(metadata, event_manager)

    widget = property_page.construct()
    description = find(widget, "description")
    description.set_text("my text")

    assert metadata.description == "my text"


def test_picture_property_select_opens_dialog(monkeypatch, diagram, event_manager):
    # Init objects
    picture = diagram.create(PictureItem)
    property_page = PicturePropertyPage(picture, event_manager)
    widget = property_page.construct()

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr(
        "gaphor.diagram.general.generalpropertypages.open_file_dialog", call
    )

    # Emulate the button click event
    button_widget = find(widget, "select-picture-button")
    button_widget.set_activate_signal_from_name("clicked")

    # Test code
    button_widget.activate()

    assert called is True


def test_picture_property_select_valid_name(monkeypatch, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr(
        "gaphor.diagram.general.generalpropertypages.error_handler", call
    )
    # Test code
    temp_image = Path("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert called is False
    assert picture.subject.name == "gaphor-24x24"


def test_picture_property_select_keep_name(monkeypatch, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    called = False

    def call(*args, **kwargs):
        nonlocal called
        called |= True

    monkeypatch.setattr(
        "gaphor.diagram.general.generalpropertypages.error_handler", call
    )

    # Test code
    picture.subject.name = "old_name"
    temp_image = Path("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert called is False
    assert picture.subject.name == "old_name"


def test_picture_property_select_replace_name_chars(diagram, event_manager):
    # Init objects
    property_page = PicturePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/diagram/general/tests/test.+gaphor$48-48.png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "test__gaphor_48-48"


def test_picture_property_select_empty_name(diagram, event_manager):
    # Init objects
    property_page = PicturePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/diagram/general/tests/.png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "_png"


def test_picture_property_select_empty_extension(diagram, event_manager):
    # Init objects
    property_page = PicturePropertyPage(None, event_manager)

    # Test code
    temp_image = Path("gaphor/diagram/general/tests/test_png")
    image_name = property_page.sanitize_image_name(temp_image)

    assert image_name == "test_png"
