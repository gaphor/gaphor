import pytest
from gi.repository import Gtk

from gaphor.ui.changeset import ChangeSet

skip_if_gtk3 = pytest.mark.skipif(
    Gtk.get_major_version() == 3,
    reason="Gtk.ListView/TreeListModel is not supported by GTK 3",
)


@skip_if_gtk3
def test_open_changeset(event_manager, element_factory):
    change_set = ChangeSet(event_manager, element_factory)

    widget = change_set.open()

    assert widget
