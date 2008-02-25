"""
The Core module provides an entry point for Gaphor's core constructs.

An average module should only need to import this module.
"""

from gaphor.application import Application
from gaphor.transaction import Transaction, transactional
from gaphor.action import action, toggle_action, radio_action, build_action_group
from gaphor.i18n import _


class inject(object):
    """
    Simple descriptor for dependency injection.
    This is technically a wrapper around Application.get_service().

    Usage::

      class A(object):
        gui_manager = inject('gui_manager')
    """
    
    def __init__(self, name):
        self._name = name
        #self._s = None
        
    def __get__(self, obj, class_=None):
        """
        Resolve a dependency, but only if we're called from an object instance.
        """
        if not obj:
            return self
        return Application.get_service(self._name)
        #if self._s is None:
        #    self._s = _Application.get_service(self._name)
        #return self._s


# vim:sw=4:et:ai
