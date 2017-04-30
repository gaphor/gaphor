"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

from __future__ import absolute_import

import gtk
import os.path

import pkg_resources

icon_theme = gtk.icon_theme_get_default()
icon_theme.append_search_path(os.path.abspath(
    pkg_resources.resource_filename('gaphor.ui', 'pixmaps')))

import re


def _repl(m):
    v = m.group(1).lower()
    return len(v) == 1 and v or '%c-%c' % tuple(v)


_repl.expr = '(.?[A-Z])'


def icon_for_element(element):
    return re.sub(_repl.expr, _repl, type(element).__name__)

# vim:sw=4:et:
