"""NamedItem diagram item
"""
# vim:sw=4:et

import itertools

import gobject
import pango
from gaphor.undomanager import get_undo_manager
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.align import ItemAlign
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.groupable import GroupBase


class TextElement(DiagramItem):
    """
    Represents one text element of diagram item, i.e. flow guard, join node
    join specification, any UML named element name, etc.

    This class references subject, which can be diagram element subject
    or LiteralSpecification. Subject attribute is watched to update text
    element on diagram.

    Objects of this class are grouped with parent with GroupBase class.

    subject:         flow guard, join node specification, etc.
    subject_attr:    subject attribute containing text value
    subject_pattern: defaults to %s, is used to render text value, i.e. for
                     join node join specification it should be set to
                     '{ joinSpec = %s }'
    """
    __metaclass__ = DiagramItemMeta

    FONT='sans 10'

    def __init__(self, attr, pattern = '%s', default = None, id = None):
        DiagramItem.__init__(self, id)

        self.subject_attr = attr
        self.subject_pattern = pattern
        self.subject_default = default

        def f(subject, pspec):
            self.set_text(getattr(subject, self.subject_attr))
            self.parent.request_update()

        # create callback method to watch for changes of subject attribute
        setattr(self, 'on_subject_notify__%s' % self.subject_attr, f)

        #self.set_flags(diacanvas.COMPOSITE)
        
        font = pango.FontDescription(self.FONT)
        #self._name = diacanvas.shape.Text()
        #self._name.set_font_description(font)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        #self._name.set_markup(False)
        #self._name_border = diacanvas.shape.Path()
        #self._name_border.set_color(diacanvas.color(128,128,128))
        #self._name_border.set_line_width(1.0)
        #self._name_bounds = (0, 0, 0, 0)

        # show name border when (parent) diagram item is selected
        self.show_border = True

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def set_text(self, txt):
        """
        Set text of text element. It is rendered with pattern.
        """
        if txt and txt != self.subject_default:
            self._name.set_text(self.subject_pattern % txt)
        else:
            self._name.set_text('')
        self.request_update()

    def postload(self):
        DiagramItem.postload(self)

    def edit(self):
        self.start_editing(self._name)

    def update_label(self, x, y):
        name_w, name_h = self.get_size()

        a = self.get_property('affine')
        self.set_property('affine', (a[0], a[1], a[2], a[3], x, y))

        # Now set width and height:
        self._name_bounds = (0, 0, name_w, name_h)

    def on_update(self, affine):
        #diacanvas.CanvasItem.on_update(self, affine)

        # bounds calculation
        b1 = self._name_bounds
        self._name_border.rectangle((b1[0], b1[1]), (b1[2], b1[3]))
        self.set_bounds(b1)

    def on_point(self, x, y):
        p = (x, y)
        drp = diacanvas.geometry.distance_rectangle_point
        return drp(self._name_bounds, p)


    def get_size(self):
        """
        Return size of text element.
        """
        return map(max, self._name.to_pango_layout(True).get_pixel_size(), (10, 10))


    def on_shape_iter(self):
        """
        Return text element text and thin border, which is used to attract
        user attention.
        """
        if self.subject:
            yield self._name
            if self.is_selected() and self.show_border:
                yield self._name_border

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        return self._name

    def on_editable_start_editing(self, shape):
        pass
        #self.preserve_property('name')


    def on_editable_editing_done(self, shape, new_text):
        """
        If subject of text element exists, then set subject attribute to
        value entered by user. If text is embedded within pattern then
        remove pattern from real text value.
        """
        if self.subject:
            if self.subject_pattern != '%s':
                # remove pattern from real text value
                s1, s2 = self.subject_pattern.split('%s')
                if new_text.startswith(s1) and new_text.endswith(s2):
                    l1, l2 = map(len, (s1, s2))
                    new_text = new_text[l1:]
                    new_text = new_text[:-l2]

            get_undo_manager().begin_transaction()
            log.debug('setting %s to %s' % (self.subject_attr, new_text))
            setattr(self.subject, self.subject_attr, new_text)
            get_undo_manager().commit_transaction()


    # notifications
    def on_subject_notify(self, pspec, notifiers=()):
        """
        Detect changes of text element subject.

        If subject does not exist then set text to empty string.
        """
        DiagramItem.on_subject_notify(self, pspec, notifiers + (self.subject_attr,))
        if self.subject:
            self.set_text(getattr(self.subject, self.subject_attr))
        else:
            self.set_text('')
        self.request_update()



from zope import interface
from gaphor.interfaces import INamedItemView


class Named(object):
    interface.implements(INamedItemView)

    NAME_FONT = 'sans bold 10'

    #def __init__(self):
        #self._name = diacanvas.shape.Text()
        #self._name.set_font_description(pango.FontDescription(self.NAME_FONT))
        #self._name.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        #self._name.set_markup(False)

    #
    # DiagramItem subject notification methods
    #
    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Subject change notification callback.
        """
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)


    def on_subject_notify__name(self, subject, pspec):
        """
        Subject name change notification callback.
        """
        assert self.subject is subject
        self.request_update()



class NamedItemMeta(DiagramItemMeta):

    def __init__(self, name, bases, data):
        super(NamedItemMeta, self).__init__(name, bases, data)
        align = ItemAlign() # center, top
        align.outside = self.s_align.outside
        if align.outside:
            align.margin = (2, ) * 4
        if data.get('__icon__', False):
            align.margin = (30, 35, 10, 35) 
            self.s_align.margin = (30, 35, 10, 35) 
        else:
            align.margin = (15, 30) * 2
        self.set_cls_align('n', align, data)

        if not hasattr(self, '__n_align__'):
            align.align = self.s_align.align

        if not hasattr(self, '__n_valign__'):
            align.valign = self.s_align.valign



class NamedItem(ElementItem, Named):
    __metaclass__ = NamedItemMeta

    popup_menu = ElementItem.popup_menu + (
        'RenameItem',
        'separator',
        'EditDelete',
        'ShowElementInTreeView'
    )

    # these values can be overriden
    WIDTH = 120
    HEIGHT = 60

    def __init__(self, id = None):
        ElementItem.__init__(self, id)
        Named.__init__(self)

        #self._border = self.create_border()
        #self._shapes.add(self._border)


    def create_border(self, border = None):
        """
        Create default border.
        """
        #if border is None:
            #border = diacanvas.shape.Path()
        #border.set_line_width(2.0)
        #self.set(width = self.WIDTH, height = self.HEIGHT)
        #return border
        pass

    def draw_border(self):
        """
        Draw border of simple named item, rectangle by default.
        """
        self._border.rectangle((0, 0), (self.width, self.height))


    def get_name_size(self): # fixme: remove this method
        return self.get_text_size(self._name)


    def update_name(self, affine):
        def set_st_pos(text, x, y, width, height):
            text.set_pos((x, y))
            text.set_max_width(width)
            text.set_max_height(height)

        nalign = self.n_align
        salign = self.s_align

        if self._has_stereotype:
            sw, sh = self.get_text_size(self._stereotype)
            nw, nh = self.get_text_size(self._name)

            width = max(sw, nw)
            height = sh + nh

            # set stereotype position
            sx, sy = salign.get_pos(self._stereotype, width, height, self.width, self.height)
            set_st_pos(self._stereotype, sx, sy, sw, sh)

            # place name below stereotype
            nx = sx + (sw - nw) / 2.0
            ny = sy + sh
            set_st_pos(self._name, nx, ny, nw, nh)

            # determine position and size of stereotype and name placed
            # together
            x = min(sx, nx)
            y = sy

            align = salign
        else:
            width, height = self.get_text_size(self._name)
            x, y = nalign.get_pos(self._name, width, height, self.width, self.height)
            set_st_pos(self._name, x, y, width, height)

            align = nalign

        if not align.outside:
            min_width, min_height = align.get_min_size(width, height)
            self.set(min_width = min_width, min_height = min_height)

        return align, x, y, width, height

    def on_update(self, affine):
        align, x, y, width, height = self.update_name(affine)

        ElementItem.on_update(self, affine)

        if align.outside:
            wx, hy = x + width, y + height
            self.set_bounds((min(0, x), min(0, y),
                max(self.width, wx), max(self.height, hy)))

        self.draw_border()
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        return itertools.chain(Named.on_shape_iter(self),
            ElementItem.on_shape_iter(self))
