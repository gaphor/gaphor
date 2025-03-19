from pathlib import Path

import pytest

from gaphor.application import Application
from gaphor.event import ModelSaved, SessionCreated


@pytest.fixture
def application():
    application = Application()
    yield application
    application.shutdown()


@pytest.mark.asyncio
async def test_service_load(application):
    """Test loading services and querying utilities."""

    session = application.new_session()

    assert session.get_service("undo_manager") is not None, (
        "Failed to load the undo manager service"
    )

    assert session.get_service("file_manager") is not None, (
        "Failed to load the file manager service"
    )


@pytest.mark.asyncio
async def test_model_loaded(application, test_models):
    session = application.new_session()
    session.event_manager.handle(
        SessionCreated(None, session, filename=test_models / "all-elements.gaphor")
    )

    assert session.filename == test_models / "all-elements.gaphor"


@pytest.mark.asyncio
async def test_model_saved(application):
    session = application.new_session()
    session.event_manager.handle(ModelSaved(Path("some_file_name")))

    assert session.filename == Path("some_file_name")


@pytest.mark.asyncio
async def test_new_session_from_template(application, test_models, event_manager):
    with (test_models / "test-model.gaphor").open(encoding="utf-8") as model:
        session = application.new_session(template=model)
        await session.get_service("event_manager").gather_tasks()

    assert any(session.get_service("element_factory").select())
