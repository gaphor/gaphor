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


def swap(list, el1, el2):
    """
    Swap two elements on the list.
    """
    i1 = list.index(el1)
    i2 = list.index(el2)
    list[i1] = el2
    list[i2] = el1


class EditableTextSupport(object):
    """
    Editable text support to allow display and edit text parts of a diagram
    item.

    Attributes:
     - _texts:       list of diagram item text elements
     - _text_groups: grouping information of text elements (None - ungrouped)
    """
    def __init__(self):
        self._texts = []
        self._text_groups = { None: [] }
        self._text_groups_sizes = {}

    def postload(self):
        super(EditableTextSupport, self).postload()

    def texts(self):
        """
        Return list of diagram item text elements.
        """
        return self._texts


    def add_text(self, attr, style=None, pattern=None, visible=None,
            editable=False, font=font.FONT):
        """
        Create and add a text element.

        For parameters description and more information see TextElement
        class documentation.

        If style information contains 'text-align-group' data, then text
        element is grouped.

        Returns created text element.
        """
        txt = TextElement(attr, style=style, pattern=pattern,
                visible=visible, editable=editable, font=font)
        self._texts.append(txt)

        # try to group text element
        gname = style and style.get('text-align-group') or None
        if gname not in self._text_groups:
            self._text_groups[gname] = []
        group = self._text_groups[gname]
        group.append(txt)

        return txt


    def remove_text(self, txt):
        """
        Remove a text element from diagram item.

        Parameters:
        - txt: text to be removed
        """
        # remove from align group
        style = txt.style
        if style and hasattr(style, 'text_align_group'):
            gname = style.text_align_group
        else:
            gname = None

        group = self._text_groups[gname]
        group.remove(txt)

        # remove text element from diagram item
        self._texts.remove(txt)


    def swap_texts(self, txt1, txt2):
        """
        Swap two text elements.
        """
        swap(self._texts, txt1, txt2)

        style = txt1.style
        if style and hasattr(style, 'text_align_group'):
            gname = style.text_align_group
        else:
            gname = None

        group = self._text_groups[gname]
        swap(group, txt1, txt2)


    def _get_visible_texts(self, texts):
        """
        Get list of visible texts.
        """
        return [txt for txt in texts if txt.is_visible()]


    def _get_text_groups(self):
        """
        Get text groups.
        """
        tg = self._text_groups
        groups = self._text_groups
        return ((name, tg[name]) for name in groups if name)


    def _set_text_sizes(self, context, texts):
        """
        Calculate size for every text in the list.

        Parameters:
         - context: cairo context
         - texts:   list of texts
        """
        cr = context.cairo
        for txt in texts:
            extents = text_extents(cr, txt.text, font=txt.font, multiline=True)
            txt.bounds.width, txt.bounds.height = extents


    def _set_text_group_size(self, context, name, texts):
        """
        Calculate size of a group.

        Parameters:
         - context: cairo context
         - name:    group name
         - texts:   list of group texts
        """
        cr = context.cairo

        texts = self._get_visible_texts(texts)

        if not texts:
            self._text_groups_sizes[name] = (0, 0)
            return

        # find maximum width and total height
        width = max(txt.bounds.width for txt in texts)
        height = sum(txt.bounds.height for txt in texts)
        self._text_groups_sizes[name] = width, height


    def pre_update(self, context):
        """
        Calculate sizes of text elements and text groups.
        """
        cr = context.cairo

        # calculate sizes of text groups
        for name, texts in self._get_text_groups():
            self._set_text_sizes(context, texts)
            self._set_text_group_size(context, name, texts)

        # calculate sizes of ungrouped texts
        texts = self._text_groups[None]
        texts = self._get_visible_texts(texts)
        self._set_text_sizes(context, texts)


    def _text_group_align(self, context, name, texts):
        """
        Align group of text elements making vertical stack of strings.

        Parameters:
         - context: cairo context
         - name:    group name
         - texts:   list of group texts
        """
        cr = context.cairo

        texts = self._get_visible_texts(texts)

        if not texts:
            return

        # align according to style of last text in the group
        style = texts[-1]._style
        extents = self._text_groups_sizes[name]
        x, y = self.text_align(extents, style.text_align,
                style.text_padding, style.text_outside)

        # stack texts
        dy = 0
        dw = extents[0]
        for txt in texts:
            bounds = txt.bounds # fixme: gaphor rectangle problem
            width, height = bounds.width, bounds.height # fixme: gaphor rectangle problem
            # center stacked texts
            txt.bounds.x = x + (dw - width) / 2.0
            txt.bounds.y = y + dy
            dy += height


    def post_update(self, context):
        """
        Calculate position and sizes of all text elements of a diagram
        item.
        """
        cr = context.cairo

        # align groups of text elements
        for name, texts in self._get_text_groups():
            assert name in self._text_groups_sizes, 'No text group "%s"' % name
            self._text_group_align(context, name, texts)

        # align ungrouped text elements
        texts = self._get_visible_texts(self._text_groups[None])
        for txt in texts:
            style = txt._style
            extents = txt.bounds.width, txt.bounds.height
            x, y = self.text_align(extents, style.text_align,
                    style.text_padding, style.text_outside)

            bounds = txt.bounds # fixme: gaphor rectangle problem
            width, height = bounds.width, bounds.height # fixme: gaphor rectangle problem
            txt.bounds.x = x
            txt.bounds.y = y


    def point(self, x, y):
        """
        Return the distance to the nearest editable and visible text
        element.
        """
        def distances():
            yield 10000.0
            for txt in self._texts:
                if txt.is_visible() and txt.editable:
                    yield distance_rectangle_point(txt.bounds, (x, y))
        return min(distances())


    def draw(self, context):
        """
        Draw all text elements of a diagram item.
        """
        cr = context.cairo
        cr.save()
        for txt in self._get_visible_texts(self._texts):
            bounds = txt.bounds
            x, y = bounds.x, bounds.y
            width, height = bounds.width, bounds.height

            if self.subject:
                text_set_font(cr, txt.font)
                text_multiline(cr, x, y, txt.text)
                cr.stroke()

            if self.subject and txt.editable \
                    and (context.hovered or context.focused):

                width = max(15, width)
                height = max(10, height)
                cr.set_line_width(0.5)
                cr.rectangle(x, y, width, height)
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
     - text:     rendered string to be displayed
     - pattern:  print pattern of text
     - editable: True if text should be editable
     - font:     text font

    See also EditableTextSupport.add_text.
    """

    bounds = property(lambda self: self._bounds)

    def __init__(self, attr, style=None, pattern=None, visible=None,
            editable=False, font=font.FONT_NAME):
        """
        Create new text element with bounds (0, 0, 10, 10) and empty text.

        Parameters:
         - visible: function, which evaluates to True/False if text should
                    be visible
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

        if visible:
            self.is_visible = visible

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

    style = property(lambda s: s._style)


    def is_visible(self):
        """
        Display text by default.
        """
        return True


# vim:sw=4:et:ai
