import pytest

from gaphor.application import Application
from gaphor.event import ActiveSessionChanged, SessionShutdown


class GtkApplicationStub:
    def __init__(self):
        self.has_quit = False

    def quit(self):
        self.has_quit = True


@pytest.fixture
def gtk_app():
    return GtkApplicationStub()


@pytest.fixture
def application(gtk_app):
    application = Application(on_quit=gtk_app.quit)
    yield application
    application.shutdown()


def two_sessions(application, gtk_app=GtkApplicationStub()):
    session1 = application.new_session(["event_manager"])

    session2 = application.new_session(["event_manager"])

    return session1, session2


def test_most_recently_created_session_is_active(application):
    session1, session2 = two_sessions(application)

    assert application.active_session is session2


def test_active_window_changed(application):
    session1, session2 = two_sessions(application)

    session1.get_service("event_manager").handle(ActiveSessionChanged(None))

    assert application.active_session is session1


def test_session_shutdown(application):
    session1, session2 = two_sessions(application)

    session2.get_service("event_manager").handle(SessionShutdown(None))

    assert len(application.sessions) == 1
    assert session1 in application.sessions


def test_all_sessions_shut_down(gtk_app, application):
    session1, session2 = two_sessions(application, gtk_app)

    session1.get_service("event_manager").handle(SessionShutdown(None))
    session2.get_service("event_manager").handle(SessionShutdown(None))

    assert len(application.sessions) == 0
    assert gtk_app.has_quit
