"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.diagram.interfaces import IEditor
from gaphor.diagram import items


class CommentItemEditor(object):
    """Text edit support for Comment item.
    """
    interface.implements(IEditor)
    component.adapts(items.CommentItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.body

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.body = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(CommentItemEditor)


class NamedItemEditor(object):
    """Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(items.NamedItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.name

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.name = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(NamedItemEditor)


class ClassifierItemEditor(object):
    interface.implements(IEditor)
    component.adapts(items.ClassifierItem)

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        self._edit = None
        name_comp_height = self._item.get_name_size()[1]
        if y < name_comp_height:
            self._edit = self._item
            return True
        y -= name_comp_height
        margin = self._item.style.compartment_margin[0]
        vspacing = self._item.style.compartment_vspacing
        for comp in self._item.compartments:
            y -= margin
            for item in comp:
                y -= vspacing
                y -= item.height
                if y < item.height:
                    self._edit = item
                    return True
            y -= margin
        return False

    def get_text(self):
        if hasattr(self._edit.subject, 'render'):
            return self._edit.subject.render()
        return self._edit.subject.name

    def get_bounds(self):
        return None

    def update_text(self, text):
        if hasattr(self._edit.subject, 'parse'):
            return self._edit.subject.parse(text)
        else:
            self._item.subject.name = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(ClassifierItemEditor)
 

class AssociationItemEditor(object):
    interface.implements(IEditor)
    component.adapts(items.AssociationItem)

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        item = self._item
        if not item.subject:
            return False
        if item.head_end.point(x, y) <= 0:
            self._edit = item.head_end
        elif item.tail_end.point(x, y) <= 0:
            self._edit = item.tail_end
        else:
            self._edit = item
        return True

    def get_text(self):
        if self._edit is self._item:
            return self._edit.subject.name
        if self._edit.get_mult():
            return self._edit.get_name() + '[' + self._edit.get_mult() + ']'
        return self._edit.get_name()

    def get_bounds(self):
        return None

    def update_text(self, text):
        if hasattr(self._edit.subject, 'parse'):
            return self._edit.subject.parse(text)
        else:
            self._item.subject.name = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(AssociationItemEditor)
    


class ForkNodeItemEditor(object):
    """Text edit support for fork node join specification.
    """
    interface.implements(IEditor)
    component.adapts(items.ForkNodeItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        """
        Get join specification text.
        """
        if self._item.subject.joinSpec:
            return self._item.subject.joinSpec.value
        else:
            return ''

    def get_bounds(self):
        return None

    def update_text(self, text):
        """
        Set join specification text.
        """
        spec = self._item.subject.joinSpec
        if not spec:
            from gaphor import resource
            factory = resource(UML.ElementFactory)
            spec = self._item.subject.joinSpec = factory.create(UML.LiteralSpecification)
            spec.value = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(ForkNodeItemEditor)

# vim:sw=4:et:ai
