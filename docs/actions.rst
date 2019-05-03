Actions, menu items, toolbars and toolboxes
===========================================

The GTK+ structure is like this::

    UIManager
        |
   ActionGroup
        |
     Action

The do_activate signal is emitted when an action is activated.

Where it should lead:
 * Actions should be coded closer to the object they are working on
    - main actions - not dependent on GUI components (load/save/new/quit)
    - main actions dependent on GUI component (sub-windows, console)
    - Item actions, act either on a diagram, the selected or focused item
      or no item.
    - diagram actions (zoom, grid) work on active diagram (tab)
    - menus and actions for diagram items through adapters

 * Actions should behave more like adapters. E.g. when a popup menu is created
   for an Association item, the menu actions should present themselves in the
   context of that menu item (with toggles set right).

    - Could be registered as adapters with a name.

 * Each window has its own action group (every item with a menu?)
 * One toplevel UIManager per window or one per application/gui_manager?
 * Normal actions can be modeled as functions. If an action is sensitive or
   visible depends on the state in the action. Hence we require the update()
   method.

 * create services for for "dynamic" menus (e.g. recent files/stereotypes)


Solution for simple actions
---------------------------

For an action to actually be useful a piece of menu xml is needed.

Hence an interface ActionProvider has to be defined::

    class ActionProvider(abc.ABC):
	menu_xml = ("The menu XML")
	action_group = ("The accompanying ActionGroup")

Support for actions can be arranged by decorating actions with an :ref:`@action <action_doc>`
decorator and let the class create an ActionGroup using some
actionGroup factory function (no inheritance needed here).

Note that ActionGroup is a GTK class and should technically only be used in the
gaphor.ui package.

Autonom controllers can be defined, which provide a piece of functionality.
They can register handlers in order to update their state.

Maybe it's nice to configure those through the egg-info system. I suppose
gaphor.service will serve well (as they need to be initialized anyway)

 * also inherit ActionProvider from IService?

::

    [gaphor.services]
    xx = gaphor.actions.whatever:SomeActionProviderClass

----

.. _action_doc:

.. autoclass:: gaphor.action.action
   :members:


Solution for context sensitive menus
------------------------------------

Context sensitive menus, such as popup menus, should be generated and switched
on and off on demand.

Technically they should be enabled through services/action-providers.

It becomes even tougher when popup menus should act on parts of a diagram item
(such as association ends). This should be avoided. It may be a good idea to
provide such functionality through a special layer on the canvas, by means of
some easy clickable buttons around the "hot spot" (we already have something
like that for text around association ends).

Scheme:

1. User selects an item and presses the right mouse button: a popup menu
   should be displayed.
2. Find the actual item (this may be a composite item of the element drawn).
   Use an IItemPicker adapter for that (if no such interface is available,
   use the item itself).
3. Find a ActionProvider adapters for the selected (focused) item.
4. Update the popup menu context (actions) for the selected item.

