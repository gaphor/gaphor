from gi.repository import Gio

from gaphor.abc import Service
from gaphor.ui.actiongroup import iter_actions


class MenuFragment(Service):
    """Menu fragments are used as extension points for plugins.

    Now they have some place to make themselves accessible to the user.
    """

    def __init__(self):
        self._menu = Gio.Menu.new()

    def shutdown(self):
        self._menu.remove_all()

    @property
    def menu(self):
        return self._menu

    def add_actions(self, action_provider, scope="win"):
        section = Gio.Menu.new()
        for _method_name, action in iter_actions(action_provider, scope):
            section.append(action.label, f"{action.scope}.{action.name}")
        if section.get_n_items():
            self._menu.append_section(None, section)

    def remove_actions(self, action_provider):
        pass
