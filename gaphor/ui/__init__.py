__all__ = [ 'command', 'namespace', 'stock' ]
from windowfactory import WindowFactory
from menufactory import MenuFactory, MenuEntry
from mainwindow import MainWindow
from diagramwindow import DiagramWindow
from diagramview import DiagramView
from treeview import *

# Add commands to the MenuFactory:
import command as c

entries = [
    ( 'FileNew',	c.NewCommand ),
    ( 'FileOpen',	c.OpenCommand ),
    ( 'FileSave',	c.SaveCommand ),
    ( 'FileSaveAs',	c.SaveAsCommand ),
    ( 'FileClose',	c.CloseCommand ),
    ( 'FileExit',	c.QuitCommand ),
    ( 'About',		c.AboutCommand )
]

mf = GaphorResource(MenuFactory)
for e in entries:
    mf.register(MenuEntry(name=e[0], command_class=e[1]))
del entries, e, mf, c
