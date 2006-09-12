"""
Common dependencies likeq dependency, usage, realization and implementation.
"""

from gaphor import resource, UML

from gaphor.diagram import Relationship
from gaphor.diagram.diagramline import DiagramLine


class DependencyRelationship(Relationship):
    """
    Relationship for dependencies including realization dependency between
    classifiers and components.
    """
    def relationship(self, line, head_subject = None, tail_subject = None):
        if line.get_dependency_type() == UML.Realization:
            args = ('realizingClassifier', None), ('abstraction', 'realization')
        else:
            args = ('supplier', 'supplierDependency'), ('client', 'clientDependency')
        args +=  head_subject, tail_subject
        return self.find(line, *args)



class DependencyItem(DiagramLine):
    """This class represents all types of dependencies.

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
        'use':        lambda self: self.dependency_type == UML.Usage,
        'realize':    lambda self: self.dependency_type == UML.Realization,
        'implements': lambda self: self.dependency_type == UML.Implementation,
    }

    relationship = DependencyRelationship()

    dependency_popup_menu = (
        'separator',
        'Dependency type', (
            'AutoDependency',
            'separator',
            'DependencyTypeDependency',
            'DependencyTypeUsage',
            'DependencyTypeRealization')
    )

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        self.dependency_type = UML.Dependency
        self.auto_dependency = True
        self._dash_style = True

    def save(self, save_func):
        DiagramLine.save(self, save_func)
        save_func('dependency_type', self.dependency_type.__name__)
        save_func('auto_dependency', self.auto_dependency)


    def load(self, name, value):
        if name == 'dependency_type':
            self.set_dependency_type(getattr(UML, value))
        elif name == 'auto_dependency':
            self.auto_dependency = eval(value)
        else:
            DiagramLine.load(self, name, value)


    def get_popup_menu(self):
        menu = DiagramLine.get_popup_menu(self)
        if self.subject:
            return menu
        else:
            return menu + self.dependency_popup_menu


    def get_dependency_type(self):
        return self.dependency_type


    def set_dependency_type(self, dependency_type=None):
        if not dependency_type and self.auto_dependency:
            dependency_type = self.determine_dependency_type(self.head.connected_to, self.tail.connected_to)
        self.dependency_type = dependency_type
        self.request_update()


    def update(self, context):
        super(DependencyItem, self).update(context)

        from interface import InterfaceItem
        dependency_type = self.dependency_type
        c1 = self.head.connected_to
        if c1 and dependency_type is UML.Usage \
           and isinstance(c1, InterfaceItem) and c1.is_folded():
            self._dash_style = False
        else:
            self._dash_style = True

    def draw_head(self, context):
        cr = context.cairo
        if self._dash_style:
            context.cairo.set_dash((), 0)
            cr.move_to(15, -6)
            cr.line_to(0, 0)
            cr.line_to(15, 6)
            cr.stroke()
        cr.move_to(0, 0)
    
    def draw(self, context):
        if self._dash_style:
            context.cairo.set_dash((7.0, 5.0), 0)
        super(DependencyItem, self).draw(context)

    #
    # Gaphor Connection Protocol
    #
    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.NamedElement)
        except AttributeError:
            return 0

    def confirm_connect_handle(self, handle):
        """See DiagramLine.confirm_connect_handle().

        In case of an Implementation, the head should be connected to an
        Interface and the tail to a BehavioredClassifier.

        TODO: Should Class also inherit from BehavioredClassifier?
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.head.connected_to
        c2 = self.tail.connected_to

        self._set_line_style(c1)


        s1 = s2 = None
        if c1:
            s1 = c1.subject
        if c2:
            s2 = c2.subject

        if self.auto_dependency:
            # when one handle is connected then it is possible to determe
            # the dependency type
            self.set_dependency_type(determine_dependency_type(s1, s2))

        if c1 and c2:
            relation = self.relationship
            if not relation:
                relation = resource(UML.ElementFactory).create(self.dependency_type)
                if self.get_dependency_type() == UML.Realization:
                    relation.realizingClassifier = s1
                    relation.abstraction = s2
                else:
                    relation.supplier = s1
                    relation.client = s2
            self.subject = relation


    def confirm_disconnect_handle(self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        #self._set_line_style()
        self.set_subject(None)
        self.request_update()


    @staticmethod
    def is_usage(s):
        """Return true if dependency should be usage dependency.
        """
        return isinstance(s, UML.Interface)


    @staticmethod
    def is_realization(ts, hs):
        """Return true if dependency should be realization dependency.
        """
        return isinstance(ts, UML.Classifier) and isinstance(hs, UML.Component)


    @staticmethod
    def determine_dependency_type(ts, hs):
        """Determine dependency type:
        - check if it is usage
        - check if it is realization
        - if none of above, then it is normal dependency

        The checks should be performed in above order. For example if ts and hs
        are Interface and Component, then we have two choices:
        - claim it is an usage (as ts is an Interface)
        - or claim it is a realization (as Interface is Classifier, too)
        In this case we want usage to win over realization.
        """
        dt = UML.Dependency
        if DependencyItem.is_usage(ts):
            dt = UML.Usage
        elif DependencyItem.is_realization(ts, hs):
            dt = UML.Realization
        return dt

# vim:sw=4:et
