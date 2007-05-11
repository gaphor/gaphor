"""
Style classes and constants.
"""

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = range(4)

# horizontal align
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = -1, 0, 1

# vertical align
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = -1, 0, 1


class Style(object):
    """
    Item style information. Style information is provided through object's
    attributes, i.e.::

        class InitialNodeItem
            __style__ = {
                'name-align': ('center', 'top'),
            }

    is translated to::

        >>> print style.name_align
        ('center', 'top')
    """
    def add(self, name, value):
        """
        Add style variable.

        Variable name can contain hyphens, which is converted to
        underscode, i.e. 'name-align' -> 'name_align'.

        @param name:  style variable name
        @param value: style variable value
        """
        name = name.replace('-', '_')
        setattr(self, name, value)

    def update(self, style):
        for name, value in style.items():
            self.add(name, value)

    def items(self):
        """
        Return iterator of (name, value) style information items.
        """
        return self.__dict__.iteritems()


def get_min_size(width, height, min_size, padding):
    """
    Get minimal size of an object using padding information. Calculated
    size cannot be smaller than specified minimal size.

    @param width:    object width
    @param height:   object height
    @param min_size: minimal size
    @param padding:  padding information as a tuple
        (top, right, bottom, left)
    """
    width  += padding[PADDING_LEFT] + padding[PADDING_RIGHT]
    height += padding[PADDING_TOP]  + padding[PADDING_BOTTOM]
    if width < min_size[0]:
        width = min_size[0]
    if height < min_size[1]:
        height = min_size[1]
    return width, height


def get_text_point(extents, width, height, align, padding, outside):
    """
    Calculate position of the text relative to containing box defined by
    tuple (0, 0, width, height).  Text is aligned using align and padding
    information. It can be also placed outside the box if ``outside''
    parameter is set to ``True''.

    Parameters:
     - extents: text extents like width, height, etc.
     - width:   width of the containing box
     - height:  height of the containing box
     - align:   text align information (center, top, etc.)
     - padding: text padding
     - outside: should text be put outside containing box
    """
    #x_bear, y_bear, w, h, x_adv, y_adv = extents
    w, h = extents

    halign, valign = align

    if outside:
        if halign == ALIGN_LEFT:
            x = -w - padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width + padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = -padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height + h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height + h + padding[PADDING_BOTTOM]
        else:
            assert False

    else:
        if halign == ALIGN_LEFT:
            x = padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width - w - padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = h + padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height + h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height - padding[PADDING_BOTTOM]
        else:
            assert False
    return x, y


def get_text_point_at_line(extents, p1, p2, align, padding):
    """
    Calculate position of the text relative to a line defined by points
    (p1, p2). Text is aligned using align and padding information. 

    Parameters:
     - extents: text extents like width, height, etc.
     - p1:      beginning of line
     - p2:      end of line
     - align:   text align information (center, top, etc.)
     - padding: text padding
    """
    w, h = extents

    halign, valign = align

    if halign == ALIGN_LEFT:
        x = p2[0] + padding[PADDING_LEFT]
        y = p2[1]
    elif halign == ALIGN_CENTER:
        x = (p1[0] - p2[0] - w) / 2
        y = (p1[1] - p2[1] - h) / 2
    elif halign == ALIGN_RIGHT:
        x = p1[0] - padding[PADDING_RIGHT]
        y = p1[1]
    else:
        assert False

    if valign == ALIGN_TOP:
        y = y + padding[PADDING_TOP]
    elif valign == ALIGN_BOTTOM:
        y = y - padding[PADDING_BOTTOM]
    else:
        assert False

    return x, y


# vim:sw=4:et
