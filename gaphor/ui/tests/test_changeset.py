from gaphor.ui.changeset import ChangeSet


def test_open_changeset(event_manager, element_factory):
    change_set = ChangeSet(event_manager, element_factory)

    widget = change_set.open()

    assert widget
