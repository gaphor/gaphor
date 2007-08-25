"""
Style classes and constants.
"""

from math import atan2, tan, pi

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = range(4)

# horizontal align
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = -1, 0, 1

# vertical align
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = -1, 0, 1



# 30 degrees
ANGLE_030 = pi / 6.0

# 150 degrees
ANGLE_150 = 150.0 / 180.0 * pi

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

    def __init__(self, *args, **kwargs):
        super(Style, self).__init__()
        for d in args:
            self.update(d)
        if kwargs:
            self.update(kwargs)

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


def get_min_size(width, height, padding):
    """
    Get minimal size of an object using padding information.

    @param width:    object width
    @param height:   object height
    @param padding:  padding information as a tuple
        (top, right, bottom, left)
    """
    width  += padding[PADDING_LEFT] + padding[PADDING_RIGHT]
    height += padding[PADDING_TOP]  + padding[PADDING_BOTTOM]
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
            y = -h -padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height - h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height + padding[PADDING_BOTTOM]
        else:
            assert False

    else:
        if halign == ALIGN_LEFT:
            x = padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2 + padding[PADDING_LEFT] - padding[PADDING_RIGHT]
        elif halign == ALIGN_RIGHT:
            x = width - w - padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height - h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height - h - padding[PADDING_BOTTOM]
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
    name_dx = 0.0
    name_dy = 0.0
    ofs = 5

    dx = float(p2[0]) - float(p1[0])
    dy = float(p2[1]) - float(p1[1])
    
    name_w, name_h = extents

    if dy == 0:
        rc = 1000.0 # quite a lot...
    else:
        rc = dx / dy
    abs_rc = abs(rc)
    h = dx > 0 # right side of the box
    v = dy > 0 # bottom side

    if abs_rc > 6:
        # horizontal line
        if h:
            name_dx = ofs
            name_dy = -ofs - name_h
        else:
            name_dx = -ofs - name_w
            name_dy = -ofs - name_h
    elif 0 <= abs_rc <= 0.2:
        # vertical line
        if v:
            name_dx = -ofs - name_w
            name_dy = ofs
        else:
            name_dx = -ofs - name_w
            name_dy = -ofs - name_h
    else:
        # Should both items be placed on the same side of the line?
        r = abs_rc < 1.0

        # Find out alignment of text (depends on the direction of the line)
        align_left = (h and not r) or (r and not h)
        align_bottom = (v and not r) or (r and not v)
        if align_left:
            name_dx = ofs
        else:
            name_dx = -ofs - name_w
        if align_bottom:
            name_dy = -ofs - name_h
        else:
            name_dy = ofs 
    return p1[0] + name_dx, p1[1] + name_dy



def get_text_point_at_line2(extents, p1, p2, align, padding):
    """
    Calculate position of the text relative to a line defined by points
    (p1, p2). Text is aligned using align and padding information. 

    TODO: merge with get_text_point_at_line function

    Parameters:
     - extents: text extents like width, height, etc.
     - p1:      beginning of line
     - p2:      end of line
     - align:   text align information (center, top, etc.)
     - padding: text padding
    """
    dx = p1[0] + p2[0]
    dy = p1[1] + p2[1]
    x0 = dx / 2.0
    y0 = dy / 2.0
    angle = atan2(p2[1] - p1[1], p2[0] - p1[0])

    width, height = extents

    # move to center and move by delta depending on line angle
    if abs(angle) % ANGLE_150 <= ANGLE_030:
        # <0, 30>, <150, 180>, <-180, -150>, <-30, 0> <- horizontal mode
        w2 = width / 2.0
        x = x0 - w2
        y = y0 - height - padding[PADDING_BOTTOM] - w2 * abs(tan(angle))
    else:
        # much better in case of vertical lines

        # determine quadrant, we are interested in 1 or 3 and 2 or 4
        # see helper tuples below
        if abs(dy) < 1e-6:
            q = 0
        else:
            q = cmp(dx / dy, 0)

        # helper tuples to move text depending on quadrant
        a = (0, 0, -1)  # width helper tuple
        b = (1, 1, -1)  # padding helper tuple

        h2 = height / 2.0
        x = x0 + b[q] * (padding[PADDING_LEFT] + h2 / abs(tan(angle))) + width * a[q]
        y = y0 - h2

    return x, y


# vim:sw=4:et
