import pytest

from gaphor.application import Application
from gaphor.event import ModelLoaded, ModelSaved


@pytest.fixture
def application():
    application = Application()
    yield application
    application.shutdown()


def test_service_load(application):
    """Test loading services and querying utilities."""

    session = application.new_session()

    assert (
        session.get_service("undo_manager") is not None
    ), "Failed to load the undo manager service"

    assert (
        session.get_service("file_manager") is not None
    ), "Failed to load the file manager service"


def test_model_loaded(application):
    session = application.new_session()
    session.event_manager.handle(ModelLoaded(None, "some_file_name"))

    assert session.filename == "some_file_name"


def test_model_saved(application):
    session = application.new_session()
    session.event_manager.handle(ModelSaved(None, "some_file_name"))

    assert session.filename == "some_file_name"
