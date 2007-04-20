"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import os, os.path
import gtk

if os.name == 'nt':
    home = 'USERPROFILE'
else:
    home = 'HOME'

user_data_dir = os.path.join(os.getenv(home), '.gaphor')


def _get_accel_map_filename():
    """
    The Gaphor accelMap file ($HOME/.gaphor/accelmap).
    """
    if not os.path.exists(user_data_dir):
        os.mkdir(user_data_dir)
    return os.path.join(user_data_dir, 'accelmap')


def load_accel_map():
    """
    Load the user accelerator map from the gaphor user home directory
    """
    filename = _get_accel_map_filename()
    if os.path.exists(filename) and os.path.isfile(filename):
        gtk.accel_map_load(filename)


def save_accel_map():
    """
    Save the contents of the GtkAccelMap to a file.
    """
    filename = _get_accel_map_filename()
    gtk.accel_map_save(filename)   


# vim:sw=4:et:
