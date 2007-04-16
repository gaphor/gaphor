"""
The Core module provides an entry point for Gaphor's core constructs.

An average module should only need to import this module.
"""

from gaphor.application import Application as _Application
#from gaphor.interfaces import IService


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
        self._inj = None
        
    def __get__(self, obj, class_=None):
        if self._inj is None:
            self._inj = _Application.get_service(self._name)
        return self._inj


# vim:sw=4:et:ai
