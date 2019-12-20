import pytest

from gaphor.misc.gidlethread import GIdleThread


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
    # GIVEN a long coroutine thread
    # WHEN waiting short timeout
    # THEN timeout is True
    assert gidle_counter


@pytest.mark.parametrize(argnames="gidle_counter", argvalues=[2], indirect=True)
def test_wait_until_finished(gidle_counter):
    # GIVEN a short coroutine thread
    # WHEN wait for coroutine to finish
    # THEN coroutine finished
    assert not gidle_counter
