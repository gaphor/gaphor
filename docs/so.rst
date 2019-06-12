Service Oriented Architecture
=============================

Gaphor has a service oriented architecture. What does this mean? Well, Gaphor
is built as a set of small islands (services). Each island provides a specific
piece of functionality. For example: a service is responsible for
loading/saving models, another for the menu structure, yet another service
handles the undo system.

Service are defined as `Egg entry points <http://peak.telecommunity.com/
DevCenter/setuptools#dynamic-discovery-of-services-and-plugins>`_.
With entry points applications can register functionality for specific
purposes. Entry points are grouped in so called *entry point groups*.
For example the `console_scripts` entry point group is used to start
an application from the command line.

Entry points, as well as all major components in Gaphor, are defined around
`Zope interfaces <http://www.zope.org/Products/ZopeInterface>`_. An interface
defines specific methods and attributes that should be implemented by the class.

Entry point groups
------------------

Gaphor defines two entry point groups:

 * gaphor.services
 * gaphor.uicomponents

Services are used to add functionality to the application.
Plug-ins should also be defined as services. E.g.::

    entry_points = {
        'gaphor.services': [
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
        ],
    },

There is a thin line between a service and a plug-in. A service typically
performs some basic need for the applications (such as the element factory
or the undo mechanism). A plug-in is more of an add-on. For example a plug-in
can depend on external libraries or provide a cross-over function between
two applications.

Interfaces
----------

Each service (and plug-in) should implement the `gaphor.abc.Service`
interface:

.. autoclass:: gaphor.abc.Service
   :members:

UI components is another piece of cake. The ``gaphor.uicomponents`` entry
point group is used to define windows and user interface functionality.
A UI component should implement the `gaphor.ui.abc.UIComponent`
interface:

.. autoclass:: gaphor.ui.abc.UIComponent
   :members:

Typically a service and UI component would like to present some actions to the
user, by means of menu entries. Every service and UI component can advertise
actions by implementing the ``gaphor.abc.ActionProvider`` interface:

.. autoclass:: gaphor.abc.ActionProvider
   :members:


Example plugin
~~~~~~~~~~~~~~

A small example is provided by means of the `Hello world plugin`.
Take a look at the files at `Github <https://github.com/amolenaar/gaphor.plugins.helloworld>`_.

The `setup.py <https://github.com/amolenaar/gaphor.plugins.helloworld/blob/master/setup.py>`_
file contains an entry point::

    entry_points = {
        'gaphor.services': [
            'helloworld = gaphor.plugins.helloworld:HelloWorldPlugin',
        ]
    }

This refers to the class ``HelloWorldPlugin`` in package/module
`gaphor.plugins.helloworld <https://github.com/amolenaar/gaphor.plugins.helloworld/blob/master/gaphor/plugins/helloworld/__init__.py>`_.

Here is a stripped version of the hello world class::



    from gaphor.abc import Service, ActionProvider
    from gaphor.core import _, action, build_action_group

    class HelloWorldPlugin(Service, ActionProvider):     # 1.


        menu_xml = """                                   # 2.
          <ui>
            <menubar name="mainwindow">
              <menu action="help">
                <menuitem action="helloworld" />
              </menu>
            </menubar>
          </ui>
        """

        def __init__(self, main_window):                 # 3.
            self.main_window = main_window
            self.action_group = build_action_group(self) # 4.

        def shutdown(self):                              # 6.
            pass

        @action(name='helloworld',                       # 7.
                label=_('Hello world'),
                tooltip=_('Every application ...'))
        def helloworld_action(self):
            main_window = self.main_window
            pass # gtk code left out

1. As stated before, a plugin should implement the ``Service`` interface.
   It also implements ``ActionProvider``, saying it has some actions to
   be performed by the user.
2. As part of the ``ActionProvider`` interface an attribute ``menu_xml``
   should be defined that contains some menu xml
   (see http://developer.gnome.org/doc/API/2.0/gtk/GtkUIManager.html#XML-UI).
3. The plugin depends on the ``main_window`` service. The ``main_window`` will
   be injected when our services is instantiated.
4. ``ActionProvider`` also requires an ``action_group`` attribute (containing
   a ``gtk.ActionGroup``). This action group is created on instantiation.
   The actions itself are defined with an ``action`` decorator (see 7).
5. Each ``Service`` has an ``init(app)`` method...
6. ... and a ``shutdown()`` method. Those can be used to create and detach
   event handlers for example.
7. The action that can be invoked. The action is defined and will be picked
   up by ``build_action_group()`` (see 4.)
