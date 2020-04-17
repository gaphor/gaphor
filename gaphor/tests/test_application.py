from gaphor.application import Application


def test_service_load():
    """Test loading services and querying utilities."""

    application = Application()
    session = application.new_session()

    assert (
        session.get_service("undo_manager") is not None
    ), "Failed to load the undo manager service"

    assert (
        session.get_service("file_manager") is not None
    ), "Failed to load the file manager service"

    application.shutdown()
