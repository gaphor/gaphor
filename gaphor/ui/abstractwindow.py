# vim:sw=4

class AbstractWindow(object):
    """
    AbstractWindow is an abstract base class for window shell related classes.
    The actual windows are created by the WindowFactory. The methods defined
    here should be overriden in window shell implementations
    """

    def get_context(self):
    	raise NotImplementedError, 'get_context() should contain a context such as main.menu'

