from gaphor.abc import ActionProvider, Service
from gaphor.action import action


class Greeter(Service, ActionProvider):
    def __init__(self, application):
        self.application = application

    @action(name="app.new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.

        This action will create a new UML model.  This will trigger a
        FileManagerStateChange event.
        """
        self.application.new_session()

    def shutdown(self):
        pass
