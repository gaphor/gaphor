"""
Interaction diagram item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP

class InteractionItem(NamedItem):

    __uml__ = UML.Interaction

    __style__ = {
        'min-size': (300, 300),
        'name-align': (ALIGN_TOP, ALIGN_LEFT),
    }

    def draw(self, context):
        super(InteractionItem, self).draw(context)
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        
        # draw pentagon
        w, h = self._header_size
        h2 = h / 2.0
        cr.move_to(0, h)
        cr.line_to(w - 4, h)
        cr.line_to(w, h2)
        cr.line_to(w, 0)
        cr.stroke()


###         self._children = []
### #    def on_subject_notify(self, pspec, notifiers=()):
### #        NamedItem.on_subject_notify(self, pspec, ('appliedStereotype',) + notifiers)
### #        self.update_stereotype()
### 
### #    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
### #        if self.subject:
### #            self.update_stereotype()
### 
###     def can_contain(self, item):
###         """Return True if item can be added as child item to the interaction.
###         """
###         return item.subject and isinstance(item.subject, (UML.Message, UML.Lifeline))
### 
###     def on_update(self, affine):
### 
###         # Center the text
###         name_width, name_height = self.get_name_size()
### 
###         self.set(min_width=name_width + InteractionItem.MARGIN_X + self.PADDING,
###                  min_height=name_height + InteractionItem.MARGIN_Y + self.PADDING)
### 
###         width = self.get_property('width')
###         height = self.get_property('height')
### 
###         self.update_name(x=self.MARGIN_X/2, y=self.MARGIN_Y/2,
###                          width=self.width, height=name_height)
### 
###         NamedItem.on_update(self, affine)
### 
###         self._border.rectangle((0,0),(width, height))
###         self.expand_bounds(1.0)
### 
###         box_h = self._title_box_height = name_height + InteractionItem.MARGIN_Y
###         box_w = self._title_box_width = name_width + InteractionItem.MARGIN_X
###         self._titleline.line(((0, box_h),
###                               (box_w - 4, box_h),
###                               (box_w, box_h - 8),
###                               (box_w, 0)))
### 
###         for child in self._children:
###             self.update_child(child, affine)
### 
### 
###     def on_point(self, x, y):
###         """Recalculate the distance from to the Interaction.
###         The distance (should be) is determined by the minimum of
###         the distances from the interaction borders and the upper left
###         box, which contains the interaction's name.
###         returns: distance (float)
###         """
###         return NamedItem.on_point(self, x, y) + 2.0
###         p = (x, y)
###         d1 = diacanvas.geometry.distance_rectangle_point((0, 0, self._title_box_width, self._title_box_height), p)
###         dlp = diacanvas.geometry.distance_line_point
###         cap_round = diacanvas.shape.CAP_ROUND
###         w = self.get_property('width')
###         h = self.get_property('height')
###         ul = (0, 0)
###         ur = (w, 0)
###         ll = (0, h)
###         lr = (w, h)
###         d2, dummy_point = dlp(ul, ur, p, 2, cap_round)
###         d3, dummy_point = dlp(ul, ll, p, 2, cap_round)
###         d4, dummy_point = dlp(ur, lr, p, 2, cap_round)
###         d5, dummy_point = dlp(ll, lr, p, 2, cap_round)
###         return min(d1, d2, d3, d4, d5) + 5.0
### 
###     def on_shape_iter(self):
###         yield self._border
###         yield self._titleline
###         for s in NamedItem.on_shape_iter(self):
###             yield s
### 
###     # Groupable
### 
###     def on_groupable_add(self, item):
###         """Add an attribute or operation.
###         """
###         self._children.append(item)
###         if self.subject and item.subject:
###             item.subject.interaction = self.subject
###         item.set_child_of(self)
###         self.request_update()
###         return 1
### 
###     def on_groupable_remove(self, item):
###         """Remove a feature subitem.
###         """
###         if item in self._children:
###             self._children.remove(item)
###             item.set_child_of(None)
###         else:
###             log.warning('feature %s not found in feature list' % item)
###             return 0
###         self.request_update()
###         #log.debug('Feature removed: %s' % item)
###         return 1
### 
###     def on_groupable_iter(self):
###         return iter(self._children)

# vim:sw=4:et
