from pathlib import Path

import pytest

import gaphor.services.properties
from gaphor.event import ModelSaved, SessionCreated


@pytest.fixture
def properties(event_manager):
    properties = gaphor.services.properties.Properties(event_manager)
    yield properties
    properties.shutdown()


def test_set_property(properties):
    properties.on_model_loaded(SessionCreated(None, None, filename="some_file_name"))

    properties.set("test", 1)

    assert properties.get("test") == 1


def test_load_properties(properties, event_manager):
    properties.set("test", 1)
    properties.on_model_saved(ModelSaved(None, "test_load_properties"))

    new_properties = gaphor.services.properties.Properties(event_manager)
    new_properties.on_model_loaded(SessionCreated(None, None, "test_load_properties"))

    assert new_properties.get("test") == 1


def test_load_of_corrupted_properties(properties, event_manager, caplog):
    properties.set("test", 1)
    properties.on_model_saved(ModelSaved(None, "test_load_properties"))
    Path(properties.filename).write_text("{ invalid content }", encoding="utf-8")

    new_properties = gaphor.services.properties.Properties(event_manager)
    new_properties.on_model_loaded(SessionCreated(None, None, "test_load_properties"))

    assert new_properties.get("test", "not set") == "not set"
    assert "Invalid syntax in property file" in caplog.text
