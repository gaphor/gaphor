import pytest

from gaphor.application import Application
from gaphor.core.modeling import Diagram
from gaphor.diagram.general import Line
from gaphor.diagram.segment import Segment
from gaphor.event import SessionShutdown
from gaphor.storage.recovery import sessions_dir, sha256sum
from gaphor.transaction import Transaction
from gaphor.ui import recover_sessions


@pytest.fixture
def application():
    app = Application()
    yield app
    app.shutdown()


def test_recovery_when_reloading_file(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    application.shutdown_session(session)

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert new_element_factory.lookup(diagram.id)


def test_recovery_when_change_is_rolled_back(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    with Transaction(session.get_service("event_manager")) as tx:
        diagram = element_factory.create(Diagram)
        tx.rollback()

    application.shutdown_session(session)

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)


def test_recovery_when_model_is_loaded_twice(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    new_session = application.new_session(filename=model_file, force=True)
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)


def test_no_recovery_for_new_session(application: Application):
    session = application.new_session()
    element_factory = session.get_service("element_factory")
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    application.shutdown_session(session)

    new_session = application.new_session()
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)


def test_no_recovery_for_saved_file(application: Application, test_models, tmp_path):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    log_file = session.get_service("recovery").event_log.log_file
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    file_manager = session.get_service("file_manager")
    file_manager.save(tmp_path / "newfile.gaphor")

    application.shutdown_session(session)

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)
    assert not log_file.exists()


def test_no_recovey_when_model_changed(application: Application, test_models, tmp_path):
    model_file = tmp_path / "testfile.gaphor"
    model_file.write_text(
        (test_models / "simple-items.gaphor").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    log_file = session.get_service("recovery").event_log.log_file
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    application.shutdown_session(session)

    # Modify model a bit
    with open(model_file, mode="a", encoding="utf-8") as f:
        f.write("\n")

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)
    assert log_file.with_suffix(".recovery.bak").exists()


def test_no_recovery_for_properly_closed_session(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    event_manager = session.get_service("event_manager")
    element_factory = session.get_service("element_factory")
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    event_manager.handle(SessionShutdown(session))

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)


@pytest.mark.parametrize(
    "errorous_line",
    [
        '[("s", "1234", "name", "value")]\n',
        '[("s", syntax error)]\n',
        "\n",
    ],
)
def test_broken_recovery_log(
    application: Application, test_models, caplog, errorous_line
):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(filename=model_file)
    element_factory = session.get_service("element_factory")
    log_file = session.get_service("recovery").event_log.log_file
    with Transaction(session.get_service("event_manager")):
        diagram = element_factory.create(Diagram)

    application.shutdown_session(session)

    with log_file.open("a", encoding="utf-8") as f:
        f.write(errorous_line)

    new_session = application.recover_session(
        session_id=session.session_id, filename=model_file
    )
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)
    assert "Could not recover model changes" in caplog.text


@pytest.mark.parametrize("template", [True, False])
def test_recover_from_session_files(application: Application, test_models, template):
    session_id = "1234"
    class_id = "9876"

    create_recovery_file(
        session_id,
        {
            "path": str(test_models / "all-elements.gaphor"),
            "sha256": sha256sum(test_models / "all-elements.gaphor"),
            "template": template,
        },
        [("c", "Class", class_id, None)],
    )
    recover_sessions(application)

    session = next(s for s in application.sessions if s.session_id == session_id)
    element_factory = session.get_service("element_factory")

    assert element_factory.lookup(class_id)


def test_recover_with_invalid_filename(application: Application):
    session_id = "1234"
    class_id = "9876"

    create_recovery_file(
        session_id,
        {
            "path": "not-a-model.gaphor",
            "sha256": "1234",
            "template": False,
        },
        [("c", "Class", class_id, None)],
    )
    recover_sessions(application)

    assert not application.sessions


def test_recover_with_invalid_sha(application: Application, test_models):
    session_id = "1234"
    class_id = "9876"

    create_recovery_file(
        session_id,
        {
            "path": str(test_models / "all-elements.gaphor"),
            "sha256": "invalid-sha",
            "template": False,
        },
        [("c", "Class", class_id, None)],
    )
    recover_sessions(application)

    session = next(s for s in application.sessions if s.session_id == session_id)
    element_factory = session.get_service("element_factory")

    assert not element_factory.lookup(class_id)


def test_recover_with_invalid_header(application: Application, test_models):
    session_id = "1234"
    class_id = "9876"

    create_recovery_file(
        session_id,
        "invalid header",
        [("c", "Class", class_id, None)],
    )
    recover_sessions(application)

    assert not application.sessions


def test_recover_with_unparseable_header(application: Application, test_models, caplog):
    session_id = "1234"
    class_id = "9876"

    create_recovery_file(
        session_id,
        {
            "path": str(test_models / "all-elements.gaphor"),
            "sha256": sha256sum(test_models / "all-elements.gaphor"),
            "template": True,
        },
        [("c", "Class", class_id, None)],
        raw_prefix="invalid",
    )
    recover_sessions(application)

    assert not application.sessions


def create_recovery_file(session_id, *lines, raw_prefix=""):
    with (sessions_dir() / f"{session_id}.recovery").open("w", encoding="utf-8") as f:
        f.write(raw_prefix)
        f.writelines(f"{repr(stmt)}\n" for stmt in lines)


def test_recovery_with_unlinked_item(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(template=model_file)
    event_manager = session.get_service("event_manager")
    element_factory = session.get_service("element_factory")
    diagram = next(element_factory.select(Diagram))

    with Transaction(event_manager):
        line = diagram.create(Line)

    with Transaction(event_manager):
        line.handles()[0].pos = (100, 100)

    with Transaction(event_manager):
        line.unlink()

    application.shutdown_session(session)

    recover_sessions(application)

    assert application.sessions


def test_recovery_with_line_segments(application: Application, test_models):
    model_file = test_models / "simple-items.gaphor"
    session = application.new_session(template=model_file)
    event_manager = session.get_service("event_manager")
    element_factory = session.get_service("element_factory")
    diagram = next(element_factory.select(Diagram))

    with Transaction(event_manager):
        line = diagram.create(Line)
        Segment(line, diagram).split_segment(0)

    with Transaction(event_manager):
        line.handles()[-1].pos = (100, 100)

    with Transaction(event_manager):
        Segment(line, diagram).merge_segment(0)

    application.shutdown_session(session)

    recover_sessions(application)

    assert application.sessions
