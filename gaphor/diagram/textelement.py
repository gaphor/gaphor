"""
Support for editable text, a part of a diagram item, i.e. name of named
item, guard of flow item, etc.
"""

from gaphor.diagram.style import Style
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_TOP
import gaphor.diagram.font as font

from gaphas.geometry import distance_rectangle_point, Rectangle
from gaphas.util import text_extents, text_align, text_multiline, \
    text_set_font


class EditableTextSupport(object):
    """
    Editable text support to allow display and edit text parts of a diagram
    item.

    Attributes:
     - _texts:       list of diagram item text elements
     - _text_groups: grouping information of text elements (None -
                     ungrouped) 
    """
    def __init__(self):
        self._texts = []
        self._text_groups = { None: [] }
        self._text_groups_sizes = {}


    def texts(self):
        """
        Return list of diagram item text elements.
        """
        return self._texts


    def add_text(self, attr, style = None, pattern = None, when = None,
            editable = False, font = font.FONT):
        """
        Create and add a text element.

        For parameters description and more information see TextElement
        class documentation.

        If style information contains 'text-align-group' data, then text
        element is grouped.

        Returns created text element.
        """
        txt = TextElement(attr, style=style, pattern=pattern, when=when,
                editable=editable, font=font)
        self._texts.append(txt)

        # try to group text element
        if style:
            gname = style.get('text-align-group')
            if gname not in self._text_groups:
                self._text_groups[gname] = []
            group = self._text_groups[gname]
            group.append(txt)

        return txt


    def _align_text_group(self, context, name):
        """
        Align group of text elements making vertical stack of strings.

        Parameters:
         - name: group name
        """
        cr = context.cairo

        group = self._text_groups[name]

        # find displayable texts
        texts = [ txt for txt in group if txt.display() ]

        # nothing to stack
        if len(texts) == 0:
            return

        # calculate text sizes
        sizes = [ text_extents(cr, txt.text, font=txt.font, multiline=True) \
                for txt in texts ]

        # find maximum width and total height
        width = max(size[0] for size in sizes)
        height = sum(size[1] for size in sizes)

        extents = (width, height)
        extents = width, height = map(max, extents, (15, 10))
        self._text_groups_sizes[name] = extents

        # align according to style of last text in the group
        style = texts[-1]._style
        x, y = self.text_align(extents, style.text_align,
                style.text_padding, style.text_outside)

        # stack all displayable texts
        dy = 0
        for i, txt in enumerate(texts):
            # calculate minimal bounds
            dw, dh = map(max, sizes[i], (15, 10))

            # center stacked texts
            txt.bounds.x0 = x + (width - dw) / 2.0
            txt.bounds.y0 = y + dy
            txt.bounds.width = dw
            txt.bounds.height = dh
            dy += dh


    def update(self, context):
        """
        Calculate position and sizes of all text elements of a diagram
        item.
        """
        cr = context.cairo
        for name in self._text_groups:
            if name is not None:
                self._align_text_group(context, name)

        # align ungrouped text elements
        for txt in self._text_groups[None]:
            if not txt.display():
                continue

            extents = text_extents(cr, txt.text, font=txt.font, multiline=True)
            extents = width, height = map(max, extents, (15, 10))

            style = txt._style
            x, y = self.text_align(extents, style.text_align,
                    style.text_padding, style.text_outside)

            txt.bounds.x0 = x
            txt.bounds.y0 = y
            txt.bounds.width = width
            txt.bounds.height = height


    def point(self, x, y):
        """
        Return the distance to the nearest text element.
        """
        distances = [10000.0]
        for txt in self._texts:
            if not txt.display():
                continue
            distances.append(distance_rectangle_point(txt.bounds, (x, y)))
        return min(distances)


    def draw(self, context):
        """
        Draw all text elements of a diagram item.
        """
        cr = context.cairo
        cr.save()
        for txt in self._texts:
            if not txt.display():
                continue
            bounds = txt.bounds
            x, y = bounds.x0, bounds.y0
            width, height = bounds.width, bounds.height

            if self.subject:
                text_set_font(cr, txt.font)
                text_multiline(cr, x, y, txt.text)

            if (context.hovered or context.focused or context.draw_all) \
                    and txt.editable:

                x, y, w, h, = x - 2, y - 2, width + 4, height + 4

                cr.set_line_width(0.5)
                cr.set_source_rgba(1.0, 1.0, 0.0, 0.2)
                cr.rectangle(x, y, w, h)
                cr.fill()

                cr.set_source_rgba(0.0, 1.0, 0.0, 0.9)
                cr.rectangle(x, y, w, h)
                cr.stroke()
        cr.restore()



class TextElement(object):
    """
    Representation of an editable text, which is part of a diagram item.

    Text element is aligned according to style information.
        
    It also displays and allows to edit value of an attribute of UML
    class (DiagramItem.subject). Attribute name can be recursive, all
    below attribute names are valid:
     - name (named item name)
     - guard.value (flow item guard)

    Attributes and properties:
     - attr:     name of displayed and edited UML class attribute
     - bounds:   text bounds
     - _style:   text style (i.e. align information, padding)
     - text:     rendered text to be displayed
     - pattern:  print pattern to display text
     - editable: True if text should be editable
     - font:     text font

    See also EditableTextSupport.add_text.
    """

    bounds = property(lambda self: self._bounds)

    def __init__(self, attr, style = None, pattern = None, when = None,
            editable = False, font = font.FONT_NAME):
        """
        Create new text element with bounds (0, 0, 10, 10) and empty text.

        Parameters:
         - when: function, which evaluates to True/False determining if text
                 should be displayed
        """
        super(TextElement, self).__init__()

        self._bounds = Rectangle(0, 0, width=10, height=0)

        # create default style for a text element
        self._style = Style()
        self._style.add('text-padding', (2, 2, 2, 2))
        self._style.add('text-align', (ALIGN_CENTER, ALIGN_TOP))
        self._style.add('text-outside', False)
        if style:
            self._style.update(style)

        self.attr = attr
        self._text = ''

        if when:
            self.display = when

        if pattern:
            self._pattern = pattern
        else:
            self._pattern = '%s'

        self.editable = editable
        self.font = font


    def _set_text(self, value):
        """
        Render text value using pattern.
        """
        self._text = value and self._pattern % value or ''


    text = property(lambda s: s._text, _set_text)


    def display(self):
        """
        Display text by default.
        """
        return True


# vim:sw=4:et:ai
