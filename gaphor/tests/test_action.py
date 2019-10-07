import pytest

from gaphor.action import action, toggle_action, radio_action


class ActionsMock:
    @action(name="simplest-action")
    def simplest_action(self):
        pass

    @action(name="tst.complete-action", label="a label", shortcut="shortcut-key")
    def complete_action(self):
        pass

    @action(name="param-action")
    def param_action(self, arg: str):
        pass


def test_simplest_action():
    action_data = ActionsMock.simplest_action.__action__

    assert action_data.name == "simplest-action"
    assert action_data.scope == "win"
    assert action_data.label is None


def test_complete_action():
    action_data = ActionsMock.complete_action.__action__

    assert action_data.name == "complete-action"
    assert action_data.scope == "tst"
    assert action_data.label == "a label"
    assert action_data.shortcut == "shortcut-key"


def test_param_action():
    action_data = ActionsMock.param_action.__action__

    assert action_data.name == "param-action"
    assert action_data.arg_type is str
