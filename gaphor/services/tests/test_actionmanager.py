import pytest
from gaphor.application import Application


@pytest.fixture
def action_manager():
    Application.init()
    return Application.get_service("action_manager")


def test_load_all_menus(action_manager):
    ui = action_manager.ui_manager.get_ui()

    assert '<menuitem name="quit" action="quit"/>' in ui, ui
    # From filemanager:
    assert '<menuitem name="file-new" action="file-new"/>' in ui, ui
    # From Undomanager
    assert '<toolitem name="edit-undo" action="edit-undo"/>' in ui, ui
