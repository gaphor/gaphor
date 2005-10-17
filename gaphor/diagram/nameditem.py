"""NamedItem diagram item
"""
# vim:sw=4:et

import itertools

import gobject
import pango
import diacanvas
from gaphor.diagram import initialize_item
from elementitem import ElementItem

class NamedItem(ElementItem, diacanvas.CanvasEditable):
    __gproperties__ = {
        'name': (gobject.TYPE_STRING, 'name', '', '', gobject.PARAM_READWRITE)
    }

    FONT = 'sans bold 10'

    popup_menu = (
        'RenameItem',
        'separator',
        'EditDelete',
        'ShowElementInTreeView'
    )

    def __init__(self, id=None):
        ElementItem.__init__(self, id)

        self._name = diacanvas.shape.Text()
        self._name.set_font_description(pango.FontDescription(self.FONT))
        self._name.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)

    def postload(self):
        ElementItem.postload(self)
        # Set values in postload, since the load function doesn't send
        # notifications.
        self._name.set_text(self.subject.name or '')

    def edit(self):
        """For diacnavas versions < 0.14.0.
        """
        self.start_editing(self._name)

    def do_set_property(self, pspec, value):
        if pspec.name == 'name':
            self.preserve_property('name')
            self.subject.name = value
        else:
            ElementItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'name':
            return self.subject.name
        else:
            return ElementItem.do_get_property(self, pspec)

    def get_name_size(self):
        """Return the width and height of the name shape.
        """
        return self._name.to_pango_layout(True).get_pixel_size()

    def update_name(self, x, y, width, height):
        self._name.set_pos((x, y))
        self._name.set_max_width(width)
        self._name.set_max_height(height)

    def on_subject_notify(self, pspec, notifiers=()):
        """See DiagramItem.on_subject_notify().
        """
        #log.info('NamedItem.on_subject_notify: %s' % str(notifiers))
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)
        self._name.set_text(self.subject and self.subject.name or '')

    def on_subject_notify__name(self, subject, pspec):
        assert self.subject is subject
        #print 'on_subject_notify__name: %s' % self.subject.name
        self._name.set_text(self.subject.name or '')
        self.request_update()

    # CanvasItem callbacks:

    #def on_update(self, affine):
    #    ElementItem.on_update(self, affine)

    def on_event (self, event):
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            self.rename()
            return True
        else:
            return ElementItem.on_event(self, event)

    def on_shape_iter(self):
        return iter([self._name])

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        #print 'on_editable_get_editable_shape', x, y
        return self._name

    def on_editable_start_editing(self, shape):
        self.preserve_property('name')

    def on_editable_editing_done(self, shape, new_text):
        self.preserve_property('name')
        if new_text != self.subject.name:
            self.canvas.get_undo_manager().begin_transaction()
            self.subject.name = new_text
            self.canvas.get_undo_manager().commit_transaction()

        self.request_update()


class SimpleNamedItem(NamedItem):
    """
    Simple named item with border.

    Deriving classes have to implement get_border and draw_border methods.

    _border - border of named item, i.e. ellipse for usecase, rectangle for
              object

    See ObjectNodeItem and UseCaseItem for examples.
    """

    WIDTH = 120
    HEIGHT = 60
    MARGIN_X = 60
    MARGIN_Y = 30

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self._border = self.get_border()
        self._border.set_line_width(2.0)
        self.set(width = self.WIDTH, height = self.HEIGHT)

    def on_update(self, affine):
        width, height = self.get_name_size()
        self.set(min_width = width + self.MARGIN_X,
            min_height = height + self.MARGIN_Y)

        self.update_name(x = 0, y = (self.height - height) / 2,
           width = self.width, height = height)

        NamedItem.on_update(self, affine)

        self.draw_border()
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        return itertools.chain(
            NamedItem.on_shape_iter(self),
            iter([self._border]))


initialize_item(NamedItem)

