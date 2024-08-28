import os

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


def test_picture_property_select_opens_dialog(mocker, diagram, event_manager):
    # Init objects
    picture = diagram.create(PictureItem)
    property_page = PicturePropertyPage(picture, event_manager)
    widget = property_page.construct()

    # Prepare mocking
    mocked_open_file_dialog = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.open_file_dialog"
    )

    # Emulate the button click event
    button_widget = find(widget, "select-picture-button")
    button_widget.set_activate_signal_from_name("clicked")

    # Test code
    button_widget.activate()

    assert mocked_open_file_dialog.called is True


def test_picture_property_select_valid_name(mocker, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    mocked_error_handler = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.error_handler"
    )

    # Test code
    temp_image = os.path.abspath("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert mocked_error_handler.called is False
    assert picture.subject.name == "gaphor-24x24"


def test_picture_property_select_keep_name(mocker, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    mocked_error_handler = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.error_handler"
    )

    # Test code
    picture.subject.name = "old_name"
    temp_image = os.path.abspath("data/logos/gaphor-24x24.png")
    property_page.open_file(temp_image)

    assert mocked_error_handler.called is False
    assert picture.subject.name == "old_name"


def test_picture_property_select_replace_name_chars(mocker, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    mocked_error_handler = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.error_handler"
    )

    # Test code
    temp_image = os.path.abspath("gaphor/diagram/general/tests/test.+gaphor$48*48.png")
    property_page.open_file(temp_image)

    assert mocked_error_handler.called is False
    assert picture.subject.name == "test__gaphor_48_48"


def test_picture_property_select_empty_name(mocker, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    mocked_error_handler = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.error_handler"
    )

    # Test code
    temp_image = os.path.abspath("gaphor/diagram/general/tests/.png")
    property_page.open_file(temp_image)

    assert mocked_error_handler.called is False
    assert picture.subject.name == "_png"


def test_picture_property_select_empty_extension(mocker, diagram, event_manager):
    # Init objects
    picture = next(
        tl for tl in general_tools.tools if tl.id == "toolbox-picture"
    ).item_factory(diagram)
    property_page = PicturePropertyPage(picture, event_manager)

    # Prepare mocking
    mocked_error_handler = mocker.patch(
        "gaphor.diagram.general.generalpropertypages.error_handler"
    )

    # Test code
    temp_image = os.path.abspath("gaphor/diagram/general/tests/test_png")
    property_page.open_file(temp_image)

    assert mocked_error_handler.called is False
    assert picture.subject.name == "test_png"
