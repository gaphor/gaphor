'''
LifelineItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from nameditem import NamedItem

# TODO: Maybe use a separate canvasItem for the line, since it creates
# some difficulty with the connect_handle() code of diacanvas.CanvasElement.

class LifelineItem(NamedItem):
    MARGIN_X = 30
    MARGIN_Y = 10

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)
        
        self._lifeline_length = 100
        self._lifeline = diacanvas.shape.Path()
        self._lifeline.set_line_width(2.0)
        self._lifeline.set_dash(0.0, (7.0, 5.0))
        self._lifeline_handle = diacanvas.Handle(self)
        self._lifeline_handle.set_property('movable', True)
        self._lifeline_handle.set_pos_i(50, 150)

#    def on_subject_notify(self, pspec, notifiers=()):
#        NamedItem.on_subject_notify(self, pspec, ('appliedStereotype',) + notifiers)
#        self.update_stereotype()

#    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
#        if self.subject:
#            self.update_stereotype()

    def on_update(self, affine):
        # Center the text
        name_width, name_height = self.get_name_size()

        self.set(min_width=name_width + LifelineItem.MARGIN_X,
                 min_height=name_height + LifelineItem.MARGIN_Y)

        width = self.get_property('width')
        height = self.get_property('height')

        self.update_name(x=0, y=height / 2 - name_height / 2,
                         width=self.width, height=name_height)

        NamedItem.on_update(self, affine)

        self._border.rectangle((0,0),(width, height))
        self.expand_bounds(1.0)

        #x, y = self._lifeline_handle.get_pos_i()
        #self._lifeline_handle.set_pos_i(width / 2, y)

        self._lifeline.line(((width / 2, height), (width / 2, height + self._lifeline_length)))

        self.set_bounds(diacanvas.geometry.rectangle_add_point(self.get_bounds(), (width / 2, height + self._lifeline_length)))

    def on_handle_motion(self, handle, x, y, event_mask):
        """Handle movements of the lifeline handle. Notw that x and y are in
        world coordinates.
        """
        if handle is self._lifeline_handle:
            x, y = self.affine_point_w2i(x, y)
            x = self.get_property('width') / 2.0
            dummy, y0 = self.handles[diacanvas.HANDLE_S].get_pos_i()
            self._lifeline_length = y - y0
            if self._lifeline_length < 10.0:
                self._lifeline_length = 10.0
                y = y0 + 10.0
            return self.affine_point_i2w(x, y)
        else:
            return NamedItem.on_handle_motion(self, handle, x, y, event_mask)

    def on_point(self, x, y):
        """Determine the distance as the distance from the box and the
        distance from the life line itself.
        """
        p = (x, y)
        w = self.get_property('width')
        h = self.get_property('height')
        handles = self.handles

        d1 = diacanvas.geometry.distance_rectangle_point((0, 0, w, h), p)
        d2, dummy_point = diacanvas.geometry.distance_line_point(handles[diacanvas.HANDLE_S].get_pos_i(), handles[-1].get_pos_i(), p, 2, diacanvas.shape.CAP_ROUND)

        return min(d1, d2)

    def on_shape_iter(self):
        yield self._border
        yield self._lifeline
        for s in NamedItem.on_shape_iter(self):
            yield s

    def inner_glue(self, handle, wx, wy):
        """Calculate the closest point on the life line (or the element).
        return a tuple (distance, point, on_element)
        """
        d1, p1 = NamedItem.on_glue(self, handle, wx, wy)

        width = self.get_property('width')
        height = self.get_property('height')
        line_start = (width / 2, height)
        line_end = (width / 2, height + self._lifeline_length)
        point = self.affine_point_w2i(wx, wy)
        d2, p2 = diacanvas.geometry.distance_line_point(line_start, line_end,
                            point, 2, diacanvas.shape.CAP_ROUND)
        if d1 < d2:
            return d1, p1, True
        else:
            return d2, self.affine_point_i2w(*p2), False

    def on_glue(self, handle, wx, wy):
        if handle.owner.allow_connect_handle(handle, self):
            d, p, dummy = self.inner_glue(handle, wx, wy)
        else:
            d, p = 10000.0, (0, 0)
        return d, p

    def on_connect_handle(self, handle):
        d, p, on_element = self.inner_glue(handle, *handle.get_pos_w())
        ret = NamedItem.on_connect_handle(self, handle)
        if not on_element:
            handle.remove_all_constraints()
            my_handles = self.handles
            handle.set_pos_w(*p)
            my_handles[diacanvas.HANDLE_S].add_line_constraint(my_handles[-1], handle)
            ret = True
        return ret

initialize_item(LifelineItem, UML.Lifeline)
