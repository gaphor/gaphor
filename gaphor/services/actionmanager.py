"""
"""

from zope import interface
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.misc.action import ActionPool

class ActionManager(object):
    """
    This service is responsible for maintaining actions.
    """

    interface.implements(IService)

    gui_manager = inject('gui_manager')

    def __init__(self):
        self._pool = ActionPool(self._action_initializer)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    def execute(self, action_id, active=None):
        return self._pool.execute(action_id, active)

    def update_actions(self):
        return self._pool.update_actions()

    def get_action(self, action_id):
        return self._pool.get_action(action_id)

    def set_action(self, action):
        self._pool.set_action(action)

    def get_slot(self, slot_id):
        return self._pool.get_slot(slot_id)

    def _action_initializer(self, action):
        # Initialize actions old style
        main_window = self.gui_manager.main_window
        try:
            action.init(main_window)
        except Exception, e:
            log.warning(str(e), e)


# vim:sw=4:et:ai
