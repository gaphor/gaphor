"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from diagramtools import PlacementTool, DefaultTool
from gaphor.core import _, inject, radio_action, build_action_group


class DiagramToolbox(object):

    def __init__(self):
        pass


# vim:sw=4:et:ai
