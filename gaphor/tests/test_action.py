import inspect

import pytest

from gaphor.action import action


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

    @action(name="fully-typed-action")
    def fully_typed_action(self, arg: str) -> None:
        pass

    @action(name="async-action")
    async def async_action(self):
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


def test_fully_typed_action():
    action_data = ActionsMock.fully_typed_action.__action__

    assert action_data.arg_type is str


def test_async_action_is_wrapped_as_synchrounous_function():
    assert not inspect.iscoroutinefunction(ActionsMock.async_action)


@pytest.mark.asyncio
async def test_async_action_schedules_task():
    mock = ActionsMock()
    action_data = ActionsMock.async_action.__action__

    mock.async_action()

    assert action_data.task


@pytest.mark.asyncio
async def test_async_action_will_not_be_executed_twice():
    mock = ActionsMock()
    action_data = ActionsMock.async_action.__action__

    mock.async_action()
    task = action_data.task
    mock.async_action()

    assert task is action_data.task
