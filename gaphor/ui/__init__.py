# vim:sw=4:et:
"""This module contains user interface related code, such as the
main screen and diagram windows.
"""

# Make sure we have GTK+ >= 2.0:
import pygtk
pygtk.require('2.0')
del pygtk

# Should we do this:
#from abstractwindow import AbstractWindow
#from mainwindow import MainWindow
#from diagramview import DiagramView
#from editorwindow import EditorWindow

# Create stock items
import stock
del stock

import os, os.path
import gtk

def _get_accel_map_filename():
    """The Gaphor accelMap file ($HOME/.gaphor/accelmap).
    """
    from gaphor import resource
    datadir = resource('UserDataDir')
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    return os.path.join(datadir, 'accelmap')


def load_accel_map():
    """Load the user accelerator map from the gaphor user home directory
    """
    filename = _get_accel_map_filename()
    if os.path.exists(filename) and os.path.isfile(filename):
        gtk.accel_map_load(filename)


def save_accel_map():
    """Save the contents of the GtkAccelMap to a file.
    """
    filename = _get_accel_map_filename()
    gtk.accel_map_save(filename)   
