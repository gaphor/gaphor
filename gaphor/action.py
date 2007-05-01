"""
Support for actions in generic files.
"""


class action(object):
    """
    Decorator. Turns a regular function (/method) into a full blown
    Action class.

    >>> class A(object):
    ...     @action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print 'action called'
    >>> a = A()
    >>> a.myaction()
    action called
    >>> is_action(a.myaction)
    True
    >>> for method in dir(A):
    ...     if is_action(getattr(A, method)):
    ...         print method
    myaction
    >>> A.myaction.name
    'my_action'
    >>> A.myaction.label
    'my action'
    """

    def __init__(self, name, label=None, **kwargs):
        self.kwargs = kwargs
        self.kwargs['name'] = name
        self.kwargs['label'] = label

    def __call__(self, func):
        func.__action__ = True
        for n, v in self.kwargs.items():
            setattr(func, n, v)
        return func
        

class toggle_action(action):

    def __init__(self, name, label=None, active=False):
        super(toggle_action, self).__init__(name, label, active=active)


class radio_action(action):

    def __init__(self, names, label=None, active=0):
        super(toggle_action, self).__init__(names[0], label, active)


def is_action(func):
    return getattr(func, '__action__', False)

def build_action_group(obj):
    """
    Build actions and an ActionGroup for each Action instance found in obj()
    (that's why Action is a class ;) ).
    """
    for name in dir(obj):
        meth = getattr(obj, name)
        if isinstance(meth, Action):
            pass # Create action / toggle / radio


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:sw=4:et:ai
