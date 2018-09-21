#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Support for actions in generic files.

See also gaphor/service/actionmanager.py for the management module.
"""

from __future__ import absolute_import, print_function

from gaphor.application import Application


class action(object):
    """
    Decorator. Turns a regular function (/method) into a full blown
    Action class.

    >>> class A(object):
    ...     @action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print('action called')
    >>> a = A()
    >>> a.myaction()
    action called
    >>> is_action(a.myaction)
    True
    >>> for method in dir(A):
    ...     if is_action(getattr(A, method)):
    ...         print(method)
    myaction
    >>> A.myaction.__action__.name
    'my_action'
    >>> A.myaction.__action__.label
    'my action'
    """

    def __init__(self, name, label=None, tooltip=None, stock_id=None, accel=None, **kwargs):
        self.name = name
        self.label = label
        self.tooltip = tooltip
        self.stock_id = stock_id
        self.accel = accel
        self.__dict__.update(kwargs)

    def __call__(self, func):
        func.__action__ = self
        return func
        

class toggle_action(action):
    """
    A toggle button can be switched on and off.
    An extra 'active' attribute is provided than gives the initial status.
    """
    def __init__(self, name, label=None, tooltip=None, stock_id=None, accel=None, active=False):
        super(toggle_action, self).__init__(name, label, tooltip, stock_id, accel=accel, active=active)


class radio_action(action):
    """
    Radio buttons take a list of names, a list of labels and a list of
    tooltips (and optionally, a list of stock_ids).
    The callback function should have an extra value property, which is
    given the index number of the activated radio button action.
    """
    def __init__(self, names, labels=None, tooltips=None, stock_ids=None, accels=None, active=0):
        super(radio_action, self).__init__(names[0], names=names, labels=labels, tooltips=tooltips, stock_ids=stock_ids, accels=accels, active=active)


def open_action(name, label=None, tooltip=None, stock_id=None, accel=None, **kwargs):
    """
    Special action used to indicate the action that is used to open (show) a UI component.

    >>> class A(object):
    ...     @open_action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print('action called')
    >>> a = A()
    >>> a.myaction()
    action called
    >>> is_action(a.myaction)
    True
    >>> for method in dir(A):
    ...     if is_action(getattr(A, method)):
    ...         print(method)
    myaction
    >>> A.myaction.__action__.name
    'my_action'
    >>> A.myaction.__action__.label
    'my action'
    >>> A.myaction.__action__.opening
    True
    """
    return action(name, label, tooltip, stock_id, accel, opening=True)


def is_action(func):
    return bool(getattr(func, '__action__', False))


def build_action_group(obj, name=None):
    """
    Build actions and a gtk.ActionGroup for each Action instance found in obj()
    (that's why Action is a class ;) ). This function requires GTK+.

    >>> class A(object):
    ...     @action(name='bar')
    ...     def bar(self): print('Say bar')
    ...     @toggle_action(name='foo')
    ...     def foo(self, active): print('Say foo', active)
    ...     @radio_action(names=('baz', 'beer'), labels=('Baz', 'Beer'))
    ...     def baz(self, value):
    ...         print('Say', value, (value and "beer" or "baz"))
    >>> group = build_action_group(A())
    Say 0 baz
    >>> len(group.list_actions())
    4
    >>> a = group.get_action('bar')
    >>> a.activate()
    Say bar
    >>> group.get_action('foo').activate()
    Say foo True
    >>> group.get_action('beer').activate()
    Say 1 beer
    >>> group.get_action('baz').activate()
    Say 0 baz
    """
    import gtk
    group = gtk.ActionGroup(name or obj)
    objtype = type(obj)

    for attrname in dir(obj):
        try:
            # Fetch the methods from the object's type instead of the object
            # itself. This prevents some desciptors (mainly gaphor.core.inject)
            # from executing.
            # Otherwise stuff like dependency resolving (=inject) may kick in
            # too early.
            method = getattr(objtype, attrname)
        except:
            continue
        act = getattr(method, '__action__', None)
        if isinstance(act, radio_action):
            actgroup = None
            if not act.labels:
                act.labels = [None] * len(act.names)
            if not act.tooltips:
                act.tooltips = [None] * len(act.names)
            if not act.stock_ids:
                act.stock_ids = [None] * len(act.names)
            if not act.accels:
                act.accels = [None] * len(act.names)
            assert len(act.names) == len(act.labels)
            assert len(act.names) == len(act.tooltips)
            assert len(act.names) == len(act.stock_ids)
            assert len(act.names) == len(act.accels)
            for i, n in enumerate(act.names):
                gtkact = gtk.RadioAction(n, act.labels[i], act.tooltips[i], act.stock_ids[i], value=i)

                if not actgroup:
                    actgroup = gtkact
                else:
                    gtkact.props.group = actgroup
                group.add_action_with_accel(gtkact, act.accels[i])

            actgroup.connect('changed', _radio_action_changed, obj, attrname)
            actgroup.set_current_value(act.active)

        elif isinstance(act, toggle_action):
            gtkact = gtk.ToggleAction(act.name, act.label, act.tooltip, act.stock_id)
            gtkact.set_property('active', act.active)
            gtkact.connect('activate', _toggle_action_activate, obj, attrname)
            group.add_action_with_accel(gtkact, act.accel)

        elif isinstance(act, action):
            gtkact = gtk.Action(act.name, act.label, act.tooltip, act.stock_id)
            try:
                activate = act.opening and _action_opening or _action_activate
            except AttributeError:
                activate = _action_activate
                
            gtkact.connect('activate', activate, obj, attrname)
            group.add_action_with_accel(gtkact, act.accel)

        elif act is not None:
            raise TypeError('Invalid action type: %s' % action)
    return group


def _action_activate(action, obj, name):
    method = getattr(obj, name)
    method()


def _action_opening(action, obj, name):
    """
    Open a new UI component if it is returned from the opening action.
    Otherwise do nothing.
    """
    method = getattr(obj, name)
    ui_comp = method()
    if ui_comp:
        Application.get_service('main_window').create_item(ui_comp)


def _toggle_action_activate(action, obj, name):
    method = getattr(obj, name)
    method(action.props.active)


def _radio_action_changed(action, current_action, obj, name):
    method = getattr(obj, name)
    method(current_action.props.value)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim:sw=4:et:ai
