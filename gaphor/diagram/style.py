"""
DEPRECATED

Style classes and constants.
"""

from gaphor.diagram.text import TextAlign, VerticalAlign

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = list(range(4))

# horizontal align - old style
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = (
    TextAlign.LEFT,
    TextAlign.CENTER,
    TextAlign.RIGHT,
)

# vertical align - old style
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = (
    VerticalAlign.TOP,
    VerticalAlign.MIDDLE,
    VerticalAlign.BOTTOM,
)


class Style:
    """
    Item style information. Style information is provided through object's
    attributes, i.e.::

    >>> from gaphor.diagram.diagramitem import DiagramItemMeta
    >>> class InitialNodeItem(object, metaclass=DiagramItemMeta):
    ...     __style__ = {
    ...         'name-align': ('center', 'top'),
    ...     }

    is translated to::

    >>> print(InitialNodeItem().style.name_align)
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
        setattr(self, name, value)

    def __setattr__(self, name, value):
        name = name.replace("-", "_")
        self.__dict__[name] = value

    def update(self, style):
        for name, value in list(style.items()):
            self.add(name, value)

    def items(self):
        """
        Return iterator of (name, value) style information items.
        """
        return iter(self.__dict__.items())


def get_min_size(width, height, padding):
    """
    Get minimal size of an object using padding information.

    @param width:    object width
    @param height:   object height
    @param padding:  padding information as a tuple
        (top, right, bottom, left)
    """
    width += padding[PADDING_LEFT] + padding[PADDING_RIGHT]
    height += padding[PADDING_TOP] + padding[PADDING_BOTTOM]
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
    # x_bear, y_bear, w, h, x_adv, y_adv = extents
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
            y = -h - padding[PADDING_TOP]
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
