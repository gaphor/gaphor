#!/usr/bin/env python

__version__ = "$Revision$"
__author__ = "EI5, eivd, Group Burgbacher - Waelti"
__date__ = "2002-02-21"

class Singleton(object):
    """
    Base class for singleton classes.
    Any class derived from this one is a singleton. You can call its
    constructor multiple times, you'll get only one instance.
    Note that __init__ must not be defined. Use init instead.

    @since 1.0
    """
    def __new__(cls, *args, **kwds):
        """
        New operator of a singleton class.
        Will return the only instance, or create it if needed.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        instance = cls.__dict__.get("__instance__")
        if instance == None:
            cls.__instance__ = instance = object.__new__(cls)
            instance.init(*args, **kwds)
        return instance

    def init(self, *args, **kwds):
        """
        Constructor of a singleton class.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        pass
