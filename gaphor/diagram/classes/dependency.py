#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License
# more details.
#
# You should have received a copy of the GNU Library General Public
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Common dependencies like dependency, usage, implementation and realization.

Dependency Type
===============
Dependency type should be determined automatically by default. User should
be able to override the dependency type.

When dependency item is connected between two items, then type of the
dependency cannot be changed. For example, if two class items are
connected, then dependency type cannot be changed to realization as this
dependency type can only exist between a component and a classifier.

Function dependency_type in model factory should be used to determine
type of a dependency in automatic way.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.diagramline import DiagramLine


class DependencyItem(DiagramLine):
    """
    Dependency item represents several types of dependencies, i.e. normal
    dependency or usage.

    Usually a dependency looks like a dashed line with an arrow head.
    The dependency can have a stereotype attached to it, stating the kind of
    dependency we're dealing with.

    In case of usage dependency connected to folded interface, the line is
    drawn as solid line without arrow head.
    """

    __uml__ = uml2.Dependency

    # do not use issubclass, because issubclass(uml2.Implementation, uml2.Realization)
    # we need to be very strict here
    __stereotype__ = {
        'use':        lambda self: self._dependency_type == uml2.Usage,
        'realize':    lambda self: self._dependency_type == uml2.Realization,
        'implements': lambda self: self._dependency_type == uml2.Implementation,
    }

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        self._dependency_type = uml2.Dependency
        self.auto_dependency = True
        self._solid = False


    def save(self, save_func):
        DiagramLine.save(self, save_func)
        save_func('auto_dependency', self.auto_dependency)


    def load(self, name, value):
        if name == 'auto_dependency':
            self.auto_dependency = eval(value)
        else:
            DiagramLine.load(self, name, value)


    def postload(self):
        if self.subject:
            dependency_type = self.subject.__class__
            DiagramLine.postload(self)
            self._dependency_type = dependency_type
        else:
            DiagramLine.postload(self)


    def set_dependency_type(self, dependency_type):
        self._dependency_type = dependency_type

    dependency_type = property(lambda s: s._dependency_type,
                               set_dependency_type)


    def draw_head(self, context):
        cr = context.cairo
        if not self._solid:
            cr.set_dash((), 0)
            cr.move_to(15, -6)
            cr.line_to(0, 0)
            cr.line_to(15, 6)
            cr.stroke()
        cr.move_to(0, 0)
    

    def draw(self, context):
        if not self._solid:
            context.cairo.set_dash((7.0, 5.0), 0)
        super(DependencyItem, self).draw(context)


# vim:sw=4:et
