# flake8: noqa F401
from gi.repository import Gtk

from gaphor.ui.abc import UIComponent

ModelBrowser: type[UIComponent]

if Gtk.get_major_version() == 3:
    from gaphor.ui.namespace import Namespace as ModelBrowser
else:
    from gaphor.ui.treecomponent import TreeComponent as ModelBrowser
