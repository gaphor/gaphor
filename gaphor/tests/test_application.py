from pathlib import Path

import pytest

from gaphor.application import Application
from gaphor.event import ModelSaved, SessionCreated


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
    session.event_manager.handle(
        SessionCreated(None, session, filename=Path("some_file_name"))
    )

    assert session.filename == Path("some_file_name")


def test_model_saved(application):
    session = application.new_session()
    session.event_manager.handle(ModelSaved(Path("some_file_name")))

    assert session.filename == Path("some_file_name")


def test_new_session_from_template(application, test_models):
    with (test_models / "test-model.gaphor").open(encoding="utf-8") as model:
        session = application.new_session(template=model)

    assert any(session.get_service("element_factory").select())
