"""NamedItem diagram item
"""
# vim:sw=4:et

import itertools

import gobject
import pango
import diacanvas
from gaphor.diagram import initialize_item
from elementitem import ElementItem
from gaphor.diagram.groupable import GroupBase
from gaphor.diagram.diagramitem import DiagramItem



class TextElement(diacanvas.CanvasItem, diacanvas.CanvasEditable, DiagramItem):
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

    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, attr, pattern = '%s', default = None, id = None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)

        self.subject_attr = attr
        self.subject_pattern = pattern
        self.subject_defualt = default

        def f(subject, pspec):
            self.set_text(getattr(subject, self.subject_attr))
            self.parent.request_update()

        # create callback method to watch for changes of subject attribute
        setattr(self, 'on_subject_notify__%s' % self.subject_attr, f)

        self.set_flags(diacanvas.COMPOSITE)
        
        font = pango.FontDescription(self.FONT)
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(font)
        self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)
        self._name_border = diacanvas.shape.Path()
        self._name_border.set_color(diacanvas.color(128,128,128))
        self._name_border.set_line_width(1.0)
        self._name_bounds = (0, 0, 0, 0)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def set_text(self, txt):
        """
        Set text of text element. It is rendered with pattern.
        """
        if txt and txt != self.subject_defualt:
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
        diacanvas.CanvasItem.on_update(self, affine)

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
            if self.is_selected():
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

            log.debug('setting %s to %s' % (self.subject_attr, new_text))
            setattr(self.subject, self.subject_attr, new_text)


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

class NamedItem(ElementItem, diacanvas.CanvasEditable):
    interface.implements(INamedItemView)
    
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



class SideNamedItem(GroupBase):
    """
    Base class for named elements, which name should be over, below or on
    on of the sides of an element.
    """
    MARGIN_X = 10
    MARGIN_Y = 10

    def __init__(self):
        GroupBase.__init__(self)

        self._name = TextElement('name')
        self.add(self._name)


    def on_update(self, affine):
        w, h = self._name.get_size()
        self._name.update_label(-w, -h)
        GroupBase.on_update(self, affine)



initialize_item(TextElement)
initialize_item(NamedItem)

