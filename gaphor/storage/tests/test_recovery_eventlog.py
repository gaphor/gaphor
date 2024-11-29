import pytest

from gaphor.storage.recovery import EventLog, sha256sum


@pytest.fixture
def test_file(tmp_path):
    f = tmp_path / "testfile"
    f.write_bytes(b"abc")
    return f


@pytest.fixture
def event_log(test_file):
    event_log = EventLog("_", test_file)
    return event_log


def test_sha256sum(tmp_path):
    tmp_file = tmp_path / "testfile"
    with tmp_file.open(mode="wb") as f:
        f.write(b"abcdefg")

    assert (
        sha256sum(tmp_file)
        == "7d1a54127b222502f5b79b5fb0803061152a44f92b37e23c6527baf665d4da9a"
    )


def test_read_event_log(event_log):
    event_log.write(["my", "line"])

    lines = list(event_log.read())

    assert ["my", "line"] in lines


def test_should_not_read_if_file_changed(event_log, test_file):
    event_log.write(["my", "line"])
    test_file.write_bytes(b"123")

    lines = list(event_log.read())

    assert ["my", "line"] not in lines


def test_clear_event_log(event_log):
    event_log.write(["my", "line"])

    event_log.clear()

    lines = list(event_log.read())

    assert not lines


def test_clear_and_add_event_log(event_log):
    event_log.write(["my", "line"])
    event_log.clear()
    event_log.write(["another line"])

    lines = list(event_log.read())

    assert ["my", "line"] not in lines
    assert ["another line"] in lines


@pytest.mark.xfail(reason="Normally a log is read first")
def test_should_not_append_if_file_changed(event_log, test_file):
    event_log.write(["my", "line"])
    event_log.close()

    # Open the log file for appending.
    test_file.write_bytes(b"123")
    event_log.write(["new", "line"])

    lines = list(event_log.read())

    assert ["my", "line"] not in lines
    assert ["new", "line"] in lines


def test_move_aside_event_log(event_log):
    event_log.write(["my", "line"])

    event_log.move_aside()

    assert not event_log.log_file.exists()
    assert event_log.log_file.with_suffix(".recovery.bak").exists()
