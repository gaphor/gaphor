"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import os
from gi.repository import Gtk
from gaphor.misc import get_config_dir


def _get_accel_map_filename():
    """
    The Gaphor accelMap file ($HOME/.gaphor/accelmap).
    """

    config_dir = get_config_dir()
    return os.path.join(config_dir, "accelmap")


def load_accel_map():
    """
    Load the user accelerator map from the gaphor user home directory
    """
    filename = _get_accel_map_filename()
    if os.path.exists(filename) and os.path.isfile(filename):
        Gtk.AccelMap.load(filename)


def save_accel_map():
    """
    Save the contents of the GtkAccelMap to a file.
    """
    filename = _get_accel_map_filename()
    Gtk.AccelMap.save(filename)


# vim:sw=4:et:
