import pytest

from gaphor.application import Application
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, ApplicationShutdown, SessionShutdown


@pytest.fixture
def application():
    application = Application()
    yield application
    application.shutdown()


def two_sessions(application):
    session1 = application.new_session(
        services=["component_registry", "event_manager", "tools_menu"]
    )

    session2 = application.new_session(
        services=["component_registry", "event_manager", "tools_menu"]
    )

    return session1, session2


def test_most_recently_created_session_is_active(application):
    _session1, session2 = two_sessions(application)

    assert application.active_session is session2


def test_active_window_changed(application):
    session1, _session2 = two_sessions(application)

    session1.get_service("event_manager").handle(ActiveSessionChanged(None))

    assert application.active_session is session1


def test_session_shutdown(application):
    session1, session2 = two_sessions(application)

    session2.get_service("event_manager").handle(SessionShutdown())

    assert len(application.sessions) == 1
    assert session1 in application.sessions


def test_all_sessions_shut_down(application):
    quit_events = []

    @event_handler(ApplicationShutdown)
    def on_quit(event):
        quit_events.append(event)

    application.event_manager.subscribe(on_quit)

    session1, session2 = two_sessions(application)

    session1.get_service("event_manager").handle(SessionShutdown())
    session2.get_service("event_manager").handle(SessionShutdown())

    assert len(application.sessions) == 0
    assert quit_events
