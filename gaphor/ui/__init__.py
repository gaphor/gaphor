"""This module contains user interface related code, such as the
main screen and diagram windows.
"""

# Make sure we have GTK+ >= 2.0:
import pygtk
pygtk.require('2.0')
del pygtk

# Should we do this:
from abstractwindow import AbstractWindow
from mainwindow import MainWindow
from diagramview import DiagramView
from editorwindow import EditorWindow

# Create stock items
import stock
del stock

