'''
PackageItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from nameditem import NamedItem

STEREOTYPE_OPEN = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class PackageItem(NamedItem):
    TAB_X=50
    TAB_Y=20
    MARGIN_X=60
    MARGIN_Y=30

    FONT_STEREOTYPE='sans 10'

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

        self.has_stereotype = False
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(pango.FontDescription(self.FONT_STEREOTYPE))
        self._stereotype.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)

    def update_stereotype(self):
        if isinstance(self.subject, UML.Profile):
            self._stereotype.set_text(STEREOTYPE_OPEN + 'profile' + STEREOTYPE_CLOSE)
            self.has_stereotype = True
        else:
            self.has_stereotype = False
        self.request_update()

    def on_subject_notify(self, pspec, notifiers=()):
        NamedItem.on_subject_notify(self, pspec, notifiers)
        self.update_stereotype()

    def on_update(self, affine):
        has_stereotype = self.has_stereotype

        st_width = st_height = 0
        if has_stereotype:
            st_width, st_height = self._stereotype.to_pango_layout(True).get_pixel_size()

        # Center the text
        name_width, name_height = self.get_name_size()

        width = max(st_width, name_width)
        height = st_height + name_height

        self.set(min_width=width + PackageItem.MARGIN_X,
                 min_height=height + PackageItem.MARGIN_Y + PackageItem.TAB_Y)

        if has_stereotype:
            self._stereotype.set_pos((0, PackageItem.TAB_Y + PackageItem.MARGIN_Y/2 - st_height))
            self._stereotype.set_max_width(self.width)
            self._stereotype.set_max_height(st_height)

        self.update_name(x=0,
                         y=PackageItem.TAB_Y + PackageItem.MARGIN_Y/2,
                         width=self.width, height=name_height)

        NamedItem.on_update(self, affine)

        o = 0.0
        h = self.height
        w = self.width
        x = PackageItem.TAB_X
        y = PackageItem.TAB_Y
        line = ((x, y), (x, o), (o, o), (o, h), (w, h), (w, y), (o, y))
        self._border.line(line)
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in NamedItem.on_shape_iter(self):
            yield s
        if self.has_stereotype:
            yield self._stereotype

initialize_item(PackageItem, UML.Package)
