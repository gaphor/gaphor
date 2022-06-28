# flake8: noqa F401
from gi.repository import Gtk

if Gtk.get_major_version() == 3:
    from gaphor.ui.namespace import Namespace as TreeComponent
else:
    from gaphor.ui.treecomponent import TreeComponent  # type: ignore[misc]
