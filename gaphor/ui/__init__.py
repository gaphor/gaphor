__all__ = [ 'command', 'commandregistry', 'namespace', 'stock' ]

import commandregistry

from mainwindow import MainWindow
from diagramwindow import DiagramWindow
from diagramview import DiagramView

# Create stock items
import stock
del stock

# Make sure build in commands are registered:
import command
del command, commandregistry
