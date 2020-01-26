from gaphor.abc import Service
from gaphor.application import Application


class Session(Service):
    """
    Application service. Get the active session.
    """

    def __init__(self, application):
        self.application = application

    def shutdown(self):
        pass

    def get_service(self, name):
        assert self.application.active_session
        return self.application.active_session.get_service(name)
