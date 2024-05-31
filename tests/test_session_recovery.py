import pytest

from gaphor.application import Application
from gaphor.core.modeling import Diagram
from gaphor.event import SessionShutdown
from gaphor.transaction import Transaction


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

    new_session = application.new_session(filename=model_file)
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

    new_session = application.new_session(filename=model_file)
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


def test_no_recovery_for_new_file(application: Application):
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

    new_session = application.new_session(filename=model_file)
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

    new_session = application.new_session(filename=model_file)
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

    new_session = application.new_session(filename=model_file)
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

    new_session = application.new_session(filename=model_file)
    new_element_factory = new_session.get_service("element_factory")

    assert not new_element_factory.lookup(diagram.id)
    assert "Could not recover model changes" in caplog.text
