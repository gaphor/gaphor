#/usr/bin/env python
# vim: sw=4:et
"""Handle menus in a MVC manner.

TODO: show tooltips in the status bar when a menu item is selected.
"""

import gobject

#from logilab.aspects.weaver import weaver

__all__ = [ 'Action', 'CheckAction', 'RadioAction', 'ActionPool', 'register_action', 'action_dependencies' ]

_registered_actions = { }

_dependent_actions = { }

class ActionError(Exception):
    pass

class Action(gobject.GObject):
    """An action. Actions are registed by register_action(). Actions should
    be part of an ActionPool. Action pools should be used to execute an action
    and update its state.
    """
    id = ''
    stock_id = ''
    tooltip = ''
    label = ''
    accel = None

    __gproperties__ = {
        'visible':      (gobject.TYPE_BOOLEAN, 'visible',
                         '', True,
                         gobject.PARAM_READWRITE),
        'sensitive':    (gobject.TYPE_BOOLEAN, 'sensitive',
                         '', True,
                         gobject.PARAM_READWRITE),
    }

    def __init__(self):
        self.__gobject_init__()
        self._visible = True
        self._sensitive = True

    visible = property(lambda self: self._visible,
                       lambda self, v: self.set_property('visible', v))
    sensitive = property(lambda self: self._sensitive,
                         lambda self, v: self.set_property('sensitive', v))

    def do_set_property(self, pspec, value):
        if pspec.name == 'visible':
            self._visible = value
        elif pspec.name == 'sensitive':
            self._sensitive = value
        else:
            raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
        if pspec.name == 'visible':
            return self._visible
        elif pspec.name == 'sensitive':
            return self._sensitive
        else:
            raise AttributeError, 'Unknown property %s' % pspec.name

    def update(self):
        """update() is called by the ActionBroker after an other action
        has been changed.
        """
        pass

    def execute(self):
        pass

gobject.type_register(Action)


class CheckAction(Action):
    """CheckActions can be turned on and off.
    """

    __gproperties__ = {
        'active':      (gobject.TYPE_BOOLEAN, 'active',
                         '', True,
                         gobject.PARAM_READWRITE)
    }

    def __init__(self):
        Action.__init__(self)
        self._active = False

    active = property(lambda self: self._active,
                      lambda self, v: self.set_property('active', v))

    def do_set_property(self, pspec, value):
        if pspec.name == 'active':
            self._active = value
        else:
            Action.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'active':
            return self._active
        else:
            return Action.do_get_property(self, pspec)

gobject.type_register(CheckAction)


class RadioAction(CheckAction):
    """RadioAction is a CheckAction, of which only one action is activated at
    a time. This is defines by a group.
    """
    group = None
    

gobject.type_register(RadioAction)


class ActionPool(object):
    """ActionPool contains a set of actions that can be executed.
    """

    def __init__(self, action_initializer):
        self.action_initializer = action_initializer
        self.actions = {}

    def get_action(self, action_id):
        """Find the action, create a new one if not found.
        """
        global _registered_actions
        try:
            action = self.actions[action_id]
        except KeyError:
            # No existing action: try to create a new one.
            try:
                action_class = _registered_actions[action_id]
            except KeyError:
                raise ActionError, 'No action registered with name "%s"' % action_id
            else:
                action = self.actions[action_id] = action_class()
                if self.action_initializer:
                    self.action_initializer(action)
                action.update()
        return action

    def execute(self, action_id):
        """Run an action, identified by its action id. If the action does
        not yet exists, it is created.

        This is the rigt way to run an action (Action.execute() should not be
        called directly!)
        """
        global _dependent_actions
        #print 'ActionPool: executing', action_id
        action = self.get_action(action_id)
        action.execute()
        # Fetch dependent actions and ask them to update themselves.
        for d in _dependent_actions.get(action_id) or ():
            try:
                dep_action = self.actions[d]
            except KeyError:
                pass # no such action in the pool
            else:
                #print 'ActionPool: updating', d
                dep_action.update()

    def get_actions(self):
        """Return the actions currently in this action pool. These are only
        the actions that have been created through get_action(), not the
        actions registered by register_action().
        """
        return self.actions.values()

    def insensivate_actions(self):
        """Make all actions insensitive. This can be used to ensure that
        no actions occur during a special big (background) action, such as
        loading or saving a model.

        Actions can be refered to their previous state by calling
        update_actions().
        """
        for action in self.actions.itervalues():
            action.sensitive = False

    def update_actions(self):
        """Update all actions.
        """
        for action in self.actions.itervalues():
            action.update()


def register_action(action, *dependency_ids):
    """Register an action so it can be looked up for on demand menu creation.
    """
    global _registered_actions
    _registered_actions[action.id] = action

    if dependency_ids:
        action_dependencies(action, *dependency_ids)


def action_dependencies(action, *dependency_ids):
    """Define a dependency for action. This means that if one of the
    dependency_ids actions is executed, action is requested to update its
    state.
    """
    global _dependent_actions

    action_id = action.id

    for di in dependency_ids:
        try:
            dependencies = _dependent_actions[di]
        except KeyError:
            # Declare a new dependency action_id -> ddi
            dependencies = [action_id]
            _dependent_actions[di] = dependencies
        else:
            if action_id not in dependencies:
                dependencies.append(action_id)

