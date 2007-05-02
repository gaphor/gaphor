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
    >>> A.myaction.__action__.name
    'my_action'
    >>> A.myaction.__action__.label
    'my action'
    """

    def __init__(self, name, label=None, tooltip=None, stock_id=None, **kwargs):
        self.name = name
        self.label = label
        self.tooltip = tooltip
        self.stock_id = stock_id
        self.__dict__.update(kwargs)

    def __call__(self, func):
        func.__action__ = self
        #for n, v in self.kwargs.items():
        #    setattr(func, n, v)
        return func
        

class toggle_action(action):
    """
    A toggle button can be switched on and off.
    An extra 'active' attribute is provided than gives the initial status.
    """
    def __init__(self, name, label=None, active=False):
        super(toggle_action, self).__init__(name, label, active=active)


class radio_action(action):
    """
    Radio buttons take a list of names, a list of labels and a list of
    tooltips (and optionally, a list of stock_ids).
    The callback function should have an extra value property, which is
    given the index number of the activated radio button action.
    """
    def __init__(self, names, labels=None, tooltips=None, stock_ids=None, active=0):
        super(radio_action, self).__init__(names[0], labels, active=active, names=names, labels=labels)


def is_action(func):
    return bool(getattr(func, '__action__', False))


def build_action_group(obj, name=None):
    """
    Build actions and an ActionGroup for each Action instance found in obj()
    (that's why Action is a class ;) ). This function requires GTK+.

    >>> class A(object):
    ...     @action(name='bar')
    ...     def bar(self): print 'Say bar'
    ...     @toggle_action(name='foo')
    ...     def foo(self): print 'Say foo'
    ...     @radio_action(names=('baz', 'beer'))
    ...     def baz(self, value):
    ...         print 'Say', value, (value and 'beer' or 'baz')
    >>> group = build_action_group(A())
    >>> len(group.list_actions())
    4
    >>> a = group.get_action('bar')
    >>> a.activate()
    Say bar
    >>> group.get_action('foo').activate()
    Say foo
    >>> group.get_action('beer').activate()
    Say 1 beer
    >>> group.get_action('baz').activate()
    Say 0 baz
    """
    import gtk
    group = gtk.ActionGroup(name)

    for attrname in dir(obj):
        method = getattr(obj, attrname)
        act = getattr(method, '__action__', None)
        if isinstance(act, radio_action):
            actgroup = None
            for i, n in enumerate(act.names):
                gtkact = gtk.RadioAction(n, act.label, act.tooltip, act.stock_id, value=i)
                if act.active == i:
                    gtkact.props.active = True

                if not actgroup:
                    actgroup = gtkact
                    gtkact.connect('changed', _radio_action_changed, obj, attrname)
                else:
                    gtkact.props.group = actgroup
                group.add_action(gtkact)
        elif isinstance(act, toggle_action):
            gtkact = gtk.ToggleAction(act.name, act.label, act.tooltip, act.stock_id)
            gtkact.set_property('active', act.active)
            gtkact.connect('activate', _action_activate, obj, attrname)
            group.add_action(gtkact)
        elif isinstance(act, action):
            gtkact = gtk.Action(act.name, act.label, act.tooltip, act.stock_id)
            gtkact.connect('activate', _action_activate, obj, attrname)
            group.add_action(gtkact)
        elif act is not None:
            raise TypeError, 'Invalid action type: %s' % action
    return group


def _action_activate(action, obj, name):
    method = getattr(obj, name)
    method()


def _radio_action_changed(action, current_action, obj, name):
    method = getattr(obj, name)
    method(current_action.props.value)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:sw=4:et:ai
