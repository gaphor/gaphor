from gaphor.core import action
from gaphor.ui.menufragment import MenuFragment


class MockService:
    @action(name="action-one", label="Action One")
    def action_one(self):
        pass

    @action(name="action-two", label="Action Two")
    def action_two(self):
        pass


def test_adding_actions():
    menu_fragment = MenuFragment()

    menu_fragment.add_actions(MockService())

    assert menu_fragment.menu.get_n_items() == 1
