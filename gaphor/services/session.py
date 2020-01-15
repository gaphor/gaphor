from gaphor.abc import Service
from gaphor.application import Application


class Session(Service):
    """
    Application service. Get the active session.
    """

    def shutdown(self):
        pass

    def get_service(self, name):
        assert Application.active_session
        return Application.active_session.get_service(name)
