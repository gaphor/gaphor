__all__ = [ 'UML', 'diagram', 'tree', 'ui', 'storage', 'plugin', 'misc' ]

# Check for GTK-2.0, since we need it anyway.
import sys, pygtk
if not sys.modules.has_key('gtk'):
    pygtk.require('2.0')
del pygtk
del sys

from gaphor import Gaphor
