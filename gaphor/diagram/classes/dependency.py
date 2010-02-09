"""
Common dependencies like dependency, usage and realization.

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

from gaphor import UML
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

    __uml__ = UML.Dependency

    # do not use issubclass, because issubclass(UML.Implementation, UML.Realization)
    # we need to be very strict here
    __stereotype__ = {
        'use':        lambda self: self._dependency_type == UML.Usage,
        'realize':    lambda self: self._dependency_type == UML.Realization,
        'implements': lambda self: self._dependency_type == UML.Implementation,
    }

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        self._dependency_type = UML.Dependency
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
