"""This module contains user interface related code, such as the
main screen and diagram windows.
"""
__all__ = [ 'command', 'commandregistry', 'namespace', 'stock' ]

# Make sure we have GTK+ >= 2.0:
import pygtk
pygtk.require('2.0')
del pygtk

import commandregistry

from abstractwindow import AbstractWindow
from mainwindow import MainWindow
from diagramwindow import DiagramWindow
from diagramview import DiagramView
from editorwindow import EditorWindow

# Create stock items
import stock
del stock

# Make sure build in commands are registered:
import command
del command, commandregistry
