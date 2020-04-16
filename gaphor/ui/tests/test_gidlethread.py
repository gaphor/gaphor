import pytest

from gaphor.ui.gidlethread import GIdleThread


def counter(count):
    for x in range(count):
        yield x


@pytest.fixture
def gidle_counter(request):
    # Setup GIdle Thread with 0.05 sec timeout
    t = GIdleThread(counter(request.param))
    t.start()
    assert t.is_alive()
    wait_result = t.wait(0.05)
    yield wait_result
    # Teardown GIdle Thread
    t.interrupt()


@pytest.mark.parametrize(argnames="gidle_counter", argvalues=[20000], indirect=True)
def test_wait_with_timeout(gidle_counter):
    assert gidle_counter


@pytest.mark.parametrize(argnames="gidle_counter", argvalues=[2], indirect=True)
def test_wait_until_finished(gidle_counter):
    assert not gidle_counter
