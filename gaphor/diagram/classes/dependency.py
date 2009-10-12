"""
Common dependencies likeq dependency, usage, realization and implementation.
"""

from gaphor import UML

#from gaphor.diagram.relationship import Relationship
from gaphor.diagram.diagramline import DiagramLine


#class DependencyRelationship(Relationship):
#    """
#    Relationship for dependencies including realization dependency between
#    classifiers and components.
#    """
#    def relationship(self, line, head_subject = None, tail_subject = None):
#        if line.get_dependency_type() == UML.Realization:
#            args = ('realizingClassifier', None), ('abstraction', 'realization')
#        else:
#            args = ('supplier', 'supplierDependency'), ('client', 'clientDependency')
#        args +=  head_subject, tail_subject
#        return self.find(line, *args)



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

    Function get_dependency_type should be used to determine automatically
    type of a dependency.

    TODO (see also InterfaceItem): When a Usage dependency is drawn and is
          connected to an InterfaceItem, draw a solid line, but stop drawing
          the line 'x' points before the last handle.
    """

    __uml__ = UML.Dependency

    # do not use issubclass, because issubclass(UML.Implementation, UML.Realization)
    # we need to be very strict here
    __stereotype__ = {
        'use':        lambda self: self._dependency_type == UML.Usage,
        'realize':    lambda self: self._dependency_type == UML.Realization,
        'implements': lambda self: self._dependency_type == UML.Implementation,
    }

#    relationship = DependencyRelationship()

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        self._dependency_type = UML.Dependency
        self.auto_dependency = True
        self._solid = False

    def save(self, save_func):
        DiagramLine.save(self, save_func)
        save_func('auto_dependency', self.auto_dependency)


    def load(self, name, value):
        #if name == 'dependency_type':
        #    self.set_dependency_type(getattr(UML, value))
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

    def get_dependency_type(self):
        return self._dependency_type


    def set_dependency_type(self, dependency_type=None):
        if not dependency_type and self.auto_dependency:
            c1 = self.canvas.get_connection(self.tail)
            c2 = self.canvas.get_connection(self.head)
            if c1 and c2:
                dt = self.determine_dependency_type(c1.item.subject, c2.item.subject)
        self._dependency_type = dt
        self.request_update()

    dependency_type = property(lambda s: s._dependency_type,
                               set_dependency_type, set_dependency_type)

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

    # todo: move methods defined below to modelfactory module

    @staticmethod
    def is_usage(s):
        """
        Return true if dependency should be usage dependency.
        """
        return isinstance(s, UML.Interface)


    @staticmethod
    def is_realization(ts, hs):
        """
        Return true if dependency should be realization dependency.
        """
        return isinstance(ts, UML.Component) and isinstance(hs, UML.Classifier)


    @staticmethod
    def determine_dependency_type(ts, hs):
        """
        Determine dependency type:

        - check if it is usage
        - check if it is realization
        - if none of above, then it is normal dependency

        The checks should be performed in above order. For example if `ts` is
        UML.Component and `hs` is UML.Interface, then there are two choices

        - dependency type is an usage (as hs is an Interface)
        - or it is a realization (as UML.Interface is UML.Classifier, too)

        In this case we want usage type to win over realization type.
        """
        dt = UML.Dependency

        log.trace('Determine dependency type for %s (tail)' \
                ' and %s (head)' % (ts, hs))

        if DependencyItem.is_usage(hs):
            dt = UML.Usage
        elif DependencyItem.is_realization(ts, hs):
            dt = UML.Realization

        log.debug('Dependency type %s' % dt)
        return dt

# vim:sw=4:et
