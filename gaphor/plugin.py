# vim:sw=4
"""
Plugin support for Gaphor.
"""

from gaphor.misc.command import Command

class PluginCommand(Command):
    """
    This is the base class for all plugin commands that are to be executed.
    PluginCommand is basically an implementation of the command pattern,
    extended by the possibility to make menu items (in)sensitive.
    """

    def __init__(self, **args):
        pass

    def get_menu_item(self):
        """
        Return the menu item representing this plugin in a menu.
        """
        pass

    def set_menu_item(self, menu_item):
        """
        Store a menu item reference in the plugin. The plugin should take care
        of making the menu item (in)sensitive at the right moment.
        The menu item is of type gaphor.ui.MenuItem (or gaphor.ui.CheckMenuItem
        for check box menu items or gaphor.ui.RadioMenuItem for radiobutton
        menu items).
        """
        pass

    def get_comment(self):
        """
        Return a piece of text to describe the menu item.
        """
        pass

    def execute(self):
        """
        Run the plugin.
        """
        pass


class Plugin(object):
    """
    Plugin class. One instance of this class is created. It is used as
    a factory for PluginCommand objects. 
    """

    def __init__(self):
        """
        Initialize a new instance of the plugin.
        """
        pass

    def get_menu_entry(self):
        """
        Return the menu entry that need to be added through this Plugin.
        It should return a (list of) tuple(s) with the format:
            (stock_id, 'menuitem name', 'icon file(s)')
        """
        pass

    def register(self):
        """
        Return a class for which the item should be displayed, or a sequence
        of classes in case it may appear for more than one item.
        For example, if this plugin should appear in the main menu (in the
        gaphor.ui.MainWindow class) this function should return
        "(gaphor.ui.MainWindow, 'path/to/menu entry')". If it should also
        appear in the diagram widget in the diagram window it should return
        "((gaphor.ui.MainWindow, 'path/to/menu entry'),
          (gaphor.ui.DiagramView, 'path/to/menu entry')).
        e.g.
            return (gaphor.ui.MainWindow, 'File/Export/SVG...')
        or
            return (gaphor.UML.Namespace, 'Edit/Set parent')
        In case this item should appear only for (popup) menu's on namespace
        elements (such as classes, packages and use cases).

        If the pathname starts with 'toolbar/' it appears in the toolbar, if
        a toolbar exists.
        """
        pass

    def get_image(self):
        """
        Return an image for the menu item. This is useful in case it appears
        in a toolbox.
        You can also return a 
        """
        pass

    def create(self, **context):
        """
        Return a new instance of a PluginCommand, context contains a buch of
        variables that can be used to set the state of the plugin.
        The variables 'class' and 'menupath' are the same as the variables
        returned by register().
        """
        pass

    def remove(self, instance):
        """
        Do some cleanup after this instance is removed.
        """
        pass

class CheckPlugin(Plugin):
    """
    Inherit from this class if your plugin should appear as a checkbox menu
    item in the menu.
    """
    pass

class RadioPlugin(Plugin):
    """
    Inherit from this class if your plugin should appear as a radio menu
    item in the menu. Note that register() should return at least two entries.
    """

    def register(self):
        """
        In case of radio menu items, more items can be returned using the
        same class, the same menu path, but a different menu item name.
        """
        pass

