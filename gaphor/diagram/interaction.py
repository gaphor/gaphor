'''
InteractionItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from nameditem import NamedItem

class InteractionItem(NamedItem):
    MARGIN_X = 10
    MARGIN_Y = 5
    PADDING = 20

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self._name.set_alignment(pango.ALIGN_LEFT)
        self.set(height=300, width=300)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)
        
        self._titleline = diacanvas.shape.Path()
        self._titleline.set_line_width(2.0)

        self._title_box_width = self.MARGIN_X * 2
        self._title_box_height = self.MARGIN_Y * 2
#    def on_subject_notify(self, pspec, notifiers=()):
#        NamedItem.on_subject_notify(self, pspec, ('appliedStereotype',) + notifiers)
#        self.update_stereotype()

#    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
#        if self.subject:
#            self.update_stereotype()

    def on_update(self, affine):
        # Center the text
        name_width, name_height = self.get_name_size()

        self.set(min_width=name_width + InteractionItem.MARGIN_X + self.PADDING,
                 min_height=name_height + InteractionItem.MARGIN_Y + self.PADDING)

        width = self.get_property('width')
        height = self.get_property('height')

        self.update_name(x=self.MARGIN_X/2, y=self.MARGIN_Y/2,
                         width=self.width, height=name_height)

        NamedItem.on_update(self, affine)

        self._border.rectangle((0,0),(width, height))
        self.expand_bounds(1.0)

        box_h = self._title_box_height = name_height + InteractionItem.MARGIN_Y
        box_w = self._title_box_width = name_width + InteractionItem.MARGIN_X
        self._titleline.line(((0, box_h),
                              (box_w - 4, box_h),
                              (box_w, box_h - 8),
                              (box_w, 0)))

    def on_point(self, x, y):
        """Recalculate the distance from to the Interaction.
        The distance (should be) is determined by the minimum of
        the distances from the interaction borders and the upper left
        box, which contains the interaction's name.
        returns: distance (float)
        """
        p = (x, y)
        d1 = diacanvas.geometry.distance_rectangle_point((0, 0, self._title_box_width, self._title_box_height), p)
        dlp = diacanvas.geometry.distance_line_point
        cap_round = diacanvas.shape.CAP_ROUND
        w = self.get_property('width')
        h = self.get_property('height')
        ul = (0, 0)
        ur = (w, 0)
        ll = (0, h)
        lr = (w, h)
        d2, dummy_point = dlp(ul, ur, p, 2, cap_round)
        d3, dummy_point = dlp(ul, ll, p, 2, cap_round)
        d4, dummy_point = dlp(ur, lr, p, 2, cap_round)
        d5, dummy_point = dlp(ll, lr, p, 2, cap_round)
        return min(d1, d2, d3, d4, d5)
        #return NamedItem.on_point(self, x, y)

    def on_shape_iter(self):
        yield self._border
        yield self._titleline
        for s in NamedItem.on_shape_iter(self):
            yield s

initialize_item(InteractionItem, UML.Interaction)
