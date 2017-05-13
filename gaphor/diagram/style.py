#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Style classes and constants.
"""

from __future__ import absolute_import
import six
from six.moves import range

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = list(range(4))

# horizontal align
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = -1, 0, 1

# vertical align
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = -1, 0, 1

# hint tuples to move text depending on quadrant
WIDTH_HINT = (0, 0, -1)    # width hint tuple
R_WIDTH_HINT = (-1, -1, 0)    # width hint tuple
PADDING_HINT = (1, 1, -1)  # padding hint tuple

EPSILON = 1e-6

class Style(object):
    """
    Item style information. Style information is provided through object's
    attributes, i.e.::

    >>> from gaphor.diagram import DiagramItemMeta
    >>> class InitialNodeItem(object):
    ...     __metaclass__ = DiagramItemMeta
    ...     __style__ = {
    ...         'name-align': ('center', 'top'),
    ...     }

    is translated to::

    >>> print InitialNodeItem().style.name_align
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
        return six.iteritems(self.__dict__)


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
    x0 = (p1[0] + p2[0]) / 2.0
    y0 = (p1[1] + p2[1]) / 2.0
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if abs(dx) < EPSILON:
        d1 = -1.0
        d2 = 1.0
    elif abs(dy) < EPSILON:
        d1 = 0.0
        d2 = 0.0
    else:
        d1 = dy / dx
        d2 = abs(d1)

    width, height = extents
    halign, valign = align

    # move to center and move by delta depending on line angle
    if d2 < 0.5774: # <0, 30>, <150, 180>, <-180, -150>, <-30, 0>
        # horizontal mode
        w2 = width / 2.0
        hint = w2 * d2

        x = x0 - w2
        if valign == ALIGN_TOP:
            y = y0 - height - padding[PADDING_BOTTOM] - hint
        else:
            y = y0 + padding[PADDING_TOP] + hint
    else:
        # much better in case of vertical lines

        # determine quadrant, we are interested in 1 or 3 and 2 or 4
        # see hint tuples below
        h2 = height / 2.0
        q = cmp(d1, 0)
        if abs(dx) < EPSILON:
            hint = 0
        else:
            hint = h2 / d2

        if valign == ALIGN_TOP:
            x = x0 + PADDING_HINT[q] * (padding[PADDING_LEFT] + hint) + width * WIDTH_HINT[q]
        else:
            x = x0 - PADDING_HINT[q] * (padding[PADDING_RIGHT] + hint) + width * R_WIDTH_HINT[q]
        y = y0 - h2

    return x, y


# vim:sw=4:et
