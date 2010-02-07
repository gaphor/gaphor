"""
Common dependencies likeq dependency, usage, realization and implementation.
"""

from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine


class DependencyItem(DiagramLine):
    """
    This class represents all types of dependencies.

    Normally a dependency looks like a dashed line with an arrow head.
    The dependency can have a stereotype attached to it, stating the kind of
    dependency we're dealing with. The dependency kind can only be changed if
    the dependency is not connected to two items.

    In the special case of an Usage dependency, where one end is
    connected to an InterfaceItem: the line is drawn as a solid line without
    arrowhead.  The Interface will draw a half a circle on the side where the
    Usage dep. is connected.

    Although it is possible to add multiple Implementation and Usage
    dependencies to an interface, it will probably not be very explaining
    (esp. Usage dependencies).

    Function dependency_type in model factory should be used to determine
    automatically type of a dependency.
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
