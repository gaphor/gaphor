"""
Plugins
=======

This module contains a bunch of standard plugins.
Plugins can be registered in Gaphor by declaring them as service entry point::

    entry_points = {
        'gaphor.services': [
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
        ],
    },


There is a thin line between a service and a plugin. A service typically performs some basic need for the applications (such as the element factory or the undo mechanism). A plugin is more of an add-on. For example a plugin can depend on external libraries or provide a cross-over function between two applications.

"""

