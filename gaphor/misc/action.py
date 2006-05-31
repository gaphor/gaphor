#/usr/bin/env python
# vim: sw=4:et
"""Handle menus in a MVC manner.

TODO: show tooltips in the status bar when a menu item is selected.
"""

import gobject
from odict import odict

__all__ = [ 'Action', 'CheckAction', 'RadioAction', 'ActionPool', 'register_action', 'action_dependencies' ]

_registered_actions = { }
_registered_slots = { }
_registered_slot_actions = { }

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
    accel = ''

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


class ObjectAction(Action):
    """An ActionObject allows you to create objects in stead of the classes
    and register them. This way you can easely create actions for
    dynamically build popup menus.
    """

    def __init__(self, id, stock_id='', tooltip='', label='', accel=''):
        Action.__init__(self)
        self._id = id
        self._stock_id = stock_id
        self._tooltip = tooltip
        self._label = label
        self._accel = accel

    id = property(lambda self: self._id)
    stock_id = property(lambda self: self._stock_id)
    tooltip = property(lambda self: self._tooltip)
    label = property(lambda self: self._label)
    accel = property(lambda self: self._accel)

    def __call__(self):
        """Return self when the object is "instantiated."
        """
        return self


class DynamicMenu(gobject.GObject):
    """An DynamicMenu is a dynamic menu (or part of a menu) that can be
    generated and changed during the lifetime of the application. A good
    example is the Placeholder.
    """

    __gsignals__ = {
        'rebuild': (gobject.SIGNAL_RUN_FIRST,
                    gobject.TYPE_NONE, ())
    }

    def __init__(self, slot_id):
        self.__gobject_init__()
        self._slot_id = slot_id

    slot_id = property(lambda self: self._slot_id)

    def rebuild(self):
        """Emit the rebuild signal.
        """
        self.emit('rebuild')

    def get_menu(self):
        """Return a tuple or list containing the menu actions.
        """
        return ()

gobject.type_register(DynamicMenu)


class SlotMenu(DynamicMenu):

    def __init__(self, slot_id):
        DynamicMenu.__init__(self, slot_id)
        self._menu = ()

    def rebuild(self):
        self._menu = ()
        DynamicMenu.rebuild(self)

    def get_menu(self):
        if not self._menu:
            self._menu = get_actions_for_slot(self.slot_id)
        #print 'menu = ', self._menu
        return self._menu

gobject.type_register(SlotMenu)


_no_default = object()

class ActionPool(object):
    """ActionPool contains a set of actions that can be executed.
    """

    def __init__(self, action_initializer):
        self.action_initializer = action_initializer
        self.actions = {}
        self.slots = {}

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

    def get_slot(self, slot_id):
        global _registered_slots
        try:
            slot = self.slots[slot_id]
        except KeyError:
            slot_class = _registered_slots.get(slot_id) or SlotMenu
            slot = slot_class(slot_id)
            self.slots[slot_id] = slot
        return slot

    def set_action(self, action):
        """Force an action class into the action pool. This is mainly used
        by Actions, which are instantiated from Slots.
        """
        self.actions[action.id] = action

    def execute(self, action_id, active=_no_default):
        """Run an action, identified by its action id. If the action does
        not yet exists, it is created.

        For check and radio actions, active may be set to set the state for the
        action.

        This is the rigt way to run an action (Action.execute() should not be
        called directly!)
        """
        global _dependent_actions, _no_default

        action = self.get_action(action_id)

        # Set state for CheckAction's:
        if isinstance(action, CheckAction) and active is not _no_default:
            action.active = bool(active)
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

    def get_action_states(self):
        """Store the states (sensitivity) of each action currently in the pool.
        States can be restored by calling set_action_states().
        """
        state = {}
        for id, action in self.actions.iteritems():
            state[id] = action.sensitive
            action.sensitive = False
        return state

    def set_action_states(self, state):
        """Restore state previously saved with get_action_states().
        """
        for action, sensitive in state.iteritems():
            self.actions[action].sensitive = sensitive

    def insensivate_actions(self):
        """Make all actions insensitive. This can be used to ensure that
        no actions occur during a special big (background) action, such as
        loading or saving a model.
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
        dependencies = _dependent_actions.setdefault(di, [])
        if action_id not in dependencies:
            dependencies.append(action_id)


# Slots

def register_slot(slot_id, slot_class=SlotMenu):
    """Register a slot. If no slot_class is provided, the SlotMenu is used.
    """
    global _registered_slots
    _registered_slots[slot_id] = slot_class


def register_action_for_slot(action, slot, *dependency_ids):
    """Register an action class for a specific slot.
    """
    global _registered_slot_actions
    #print 'Register action %s for slot %s' % (action.id, slot)
    register_action(action, *dependency_ids)
    path = slot.split('/')
    slot = _registered_slot_actions
    if path[0].startswith('<') and path[0].endswith('>'):
        path[0] = path[0][1:-1]
    for p in path:
        slot = slot.setdefault(p, {})
    slot[action.id] = None
    #import pprint
    #pprint.pprint(_registered_slot_actions)


def unregister_action_for_slot(action, slot):
    global _registered_slot_actions
    path = slot.split('/')
    slot = _registered_slot_actions
    if path[0].startswith('<') and path[0].endswith('>'):
        path[0] = path[0][1:-1]
    for p in path:
        slot = _registered_slot_actions.setdefault(p, {})
    del slot[action.id]


def get_actions_for_slot(slot):
    """Return a the action ids for a specific slot as a tuple-menu.
    E.g.
      ('DummyAction',
       'submenu', (
           'DummySubAction,))
    """
    global _registered_slot_actions
    def get_actions_tuple(d):
        l = []
        for key, val in d.iteritems():
            l.append(key)
            if val:
                l.append(get_actions_tuple(val))
        return tuple(l)
    return get_actions_tuple(_registered_slot_actions.get(slot) or {})

