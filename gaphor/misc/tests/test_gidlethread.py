from gaphor.misc.gidlethread import GIdleThread


def test_wait_with_timeout():
    # GIVEN a running gidlethread
    def counter(max):
        for x in range(max):
            yield x

    t = GIdleThread(counter(20000))
    t.start()
    assert t.is_alive()
    # WHEN waiting for 0.01 sec timeout
    wait_result = t.wait(0.01)
    # THEN timeout
    assert wait_result


def test_wait_until_finished():
    # GIVEN a short coroutine thread
    def counter(max):
        for x in range(max):
            yield x

    t = GIdleThread(counter(2))
    t.start()
    assert t.is_alive()
    # WHEN wait for coroutine to finish
    wait_result = t.wait(0.01)
    # THEN coroutine finished
    assert not wait_result
