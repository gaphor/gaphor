from gaphor.ui.statuswindow import StatusWindow


def test_status_window():
    status_window = StatusWindow("title", "message")

    assert status_window.progress_bar
    assert status_window.window
