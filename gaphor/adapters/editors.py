"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.core import inject
from gaphor.UML.umllex import render_attribute
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
        self._item.request_update()

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(NamedItemEditor)


class ObjectNodeItemEditor(NamedItemEditor):
    component.adapts(items.ObjectNodeItem)

    def __init__(self, item):
        super(ObjectNodeItemEditor, self).__init__(item)
        self.edit_tag = False

    def is_editable(self, x, y):
        self.edit_tag = (x, y) in self._item.tag_bounds
        return True

    def get_text(self):
        if self.edit_tag:
            return self._item.subject.upperBound.value
        else:
            return super(ObjectNodeItemEditor, self).get_text()

    def update_text(self, text):
        if self.edit_tag:
            self._item.subject.upperBound.value = text
        else:
            return super(ObjectNodeItemEditor, self).update_text(text)
        self._item.request_update()

component.provideAdapter(ObjectNodeItemEditor)


class FlowItemEditor(object):
    """Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(items.FlowItem)

    def __init__(self, item):
        self._item = item
        self.edit_name = False
        self.edit_guard = False

    def is_editable(self, x, y):
        if not self._item.subject:
            return False
        if (x, y) in self._item.name_bounds:
            self.edit_name = True
        elif (x, y) in self._item.guard_bounds:
            self.edit_guard = True
        return self.edit_name or self.edit_guard

    def get_text(self):
        if self.edit_name:
            return self._item.subject.name
        elif self.edit_guard:
            return self._item.subject.guard.value

    def get_bounds(self):
        return None

    def update_text(self, text):
        if self.edit_name:
            self._item.subject.name = text
        elif self.edit_guard:
            self._item.subject.guard.value = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(FlowItemEditor)


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
        if self._item.drawing_style not in (items.ClassifierItem.DRAW_COMPARTMENT, items.ClassifierItem.DRAW_COMPARTMENT_ICON):
            self._edit = self._item
            return True

        self._edit = None
        # Edit is in name compartment -> edit name
        name_comp_height = self._item.get_name_size()[1]
        if y < name_comp_height:
            self._edit = self._item
            return True

        padding = self._item.style.compartment_padding
        vspacing = self._item.style.compartment_vspacing
        
        # place offset at top of first comparement
        y -= name_comp_height
        y += vspacing / 2.0
        for comp in self._item.compartments:
            if not comp.visible:
                continue
            y -= padding[0]
            for item in comp:
                if y < item.height:
                    self._edit = item
                    return True
                y -= item.height
                y -= vspacing
            y -= padding[2]
            # Compensate for last substraction action
            y += vspacing
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
        return render_attribute(self._edit.subject)

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

    element_factory = inject('element_factory')

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
            spec = self._item.subject.joinSpec = self.element_factory.create(UML.LiteralSpecification)
            spec.value = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(ForkNodeItemEditor)

# vim:sw=4:et:ai
