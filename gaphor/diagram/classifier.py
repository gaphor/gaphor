"""
Classifier diagram item.
"""

import itertools

from gaphas.util import text_extents, text_align, text_set_font
from gaphas.state import observed, reversible_property
from gaphor import UML
from gaphor.i18n import _

from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.feature import FeatureItem
from gaphor.diagram.style import get_min_size

import font

class Compartment(list):
    """
    Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.visible = True
        self.width = 0
        self.height = 0

    def save(self, save_func):
        #log.debug('Compartment.save: %s' % self)
        for item in self:
            save_func(None, item)

    def has_item(self, item):
        """
        Check if the compartment already contains an item with the
        same subject as item.
        """
        s = item.subject
        local_elements = [f.subject for f in self]
        return s and s in local_elements

    def get_size(self):
        """
        Get width, height of the compartment. pre_update should have
        been called so widthand height have been calculated.
        """
        if self.visible:
            return self.width, self.height
        else:
            return 0, 0

    def pre_update(self, context):
        """
        Pre update, determine width and height of the compartment.
        """
        self.width = self.height = 0
        cr = context.cairo
        for item in self:
            item.pre_update(context)
        
        if self:
            # self (=list) contains items
            sizes = [ (0, 0) ] # to not throw exceptions by max and sum
            sizes.extend(f.get_size(True) for f in self)
            self.width = max(size[0] for size in sizes)
            self.height = sum(size[1] for size in sizes)
            vspacing = self.owner.style.compartment_vspacing
            self.height += vspacing * (len(sizes) - 1)

        padding = self.owner.style.compartment_padding
        self.width += padding[1] + padding[3]
        self.height += padding[0] + padding[2]

    def update(self, context):
        for item in self:
            item.update(context)

    def draw(self, context):
        cr = context.cairo
        padding = self.owner.style.compartment_padding
        vspacing = self.owner.style.compartment_vspacing
        cr.translate(padding[1], padding[0])
        offset = 0
        for item in self:
            cr.save()
            try:
                cr.translate(0, offset)
                #cr.move_to(0, offset)
                item.draw(context)
                offset += vspacing + item.height
            finally:
                cr.restore()

    def item_at(self, x, y):
        if 0 > x > self.width:
            return None
        
        padding = self.owner.style.compartment_padding
        height = padding[0]
        if y < height:
            return None

        vspacing = self.owner.style.compartment_vspacing
        for f in self:
            w, h = f.get_size(True)
            height += h + vspacing
            if y < height:
                return f
        return None


class ClassifierItem(NamedItem):
    """
    This item visualizes a Class instance.

    A ClassifierItem is a superclass for (all) Classifier like objects,
    such as Class, Interface, Component and Actor.

    ClassifierItem controls the stereotype, namespace and owning package.

    A classifier has three drawing style (ClassifierItem.drawing_style):
     - The comparttment view, as often used by Classes
     - A compartment view, but with a little stereotype icon in the right corner
     - One big icon, as used by Actors and sometimes interfaces.

    To support this behavior a few helper methods are defined which can be
    called/overridden:
     - update_compartment_icon (box-style with small icon (see ComponentItem))
     - update_icon (does nothing by default, an impl. should be provided by
                    subclasses (see ActorItem))
    """

    # Do not use preset drawing style
    DRAW_NONE = 0
    # Draw the famous box style
    DRAW_COMPARTMENT = 1
    # Draw compartment with little icon in upper right corner
    DRAW_COMPARTMENT_ICON = 2
    # Draw as icon
    DRAW_ICON = 3

    __style__ = {
        'min-size': (100, 50),
        'icon-size': (20, 20),
        'from-padding': (7, 2, 7, 2),
        'compartment-padding': (5, 5, 5, 5), # (top, right, bottom, left)
        'compartment-vspacing': 3,
        'name-padding': (10, 10, 10, 10),
        'stereotype-padding': (10, 10, 2, 10),
    }
    # Default size for small icons
    ICON_WIDTH    = 15
    ICON_HEIGHT   = 25
    ICON_MARGIN_X = 10
    ICON_MARGIN_Y = 10

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self._compartments = []

        self._drawing_style = ClassifierItem.DRAW_NONE


    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'drawing-style')
        NamedItem.save(self, save_func)

    def postload(self):
        NamedItem.postload(self)
        self.on_subject_notify__isAbstract(self.subject)

    @observed
    def set_drawing_style(self, style):
        """
        Set the drawing style for this classifier: DRAW_COMPARTMENT,
        DRAW_COMPARTMENT_ICON or DRAW_ICON.
        """
        if style != self._drawing_style:
            self._drawing_style = style
            self.request_update()

        if self._drawing_style == self.DRAW_COMPARTMENT:
            self.draw       = self.draw_compartment
            self.pre_update = self.pre_update_compartment
            self.update     = self.update_compartment

        elif self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.draw       = self.draw_compartment_icon
            self.pre_update = self.pre_update_compartment_icon
            self.update     = self.update_compartment_icon

        elif self._drawing_style == self.DRAW_ICON:
            self.draw       = self.draw_icon
            self.pre_update = self.pre_update_icon
            self.update     = self.update_icon


    drawing_style = reversible_property(lambda self: self._drawing_style, set_drawing_style)


    def create_compartment(self, name):
        """
        Create a new compartment. Compartments contain data such as
        attributes and operations.

        It is common to create compartments during the construction of the
        diagram item. Their visibility can be toggled by Compartment.visible.
        """
        c = Compartment(name, self)
        self._compartments.append(c)
        return c

    compartments = property(lambda s: s._compartments)

    def sync_uml_elements(self, elements, compartment, creator=None):
        """
        This method synchronized a list of elements with the items
        in a compartment. A creator-function should be passed which is used
        for creating new compartment items.

        @elements: the list of attributes or operations in the model
        @compartment: our local representation
        @creator: factory method for creating new attr. or oper.'s
        """
        # extract the UML elements from the compartment
        local_elements = [f.subject for f in compartment]

        # map local element with compartment element
        mapping = dict(zip(local_elements, compartment))

        to_add = [el for el in elements if el not in local_elements]

        # sync local elements with elements
        del compartment[:]

        for el in elements:
            if el in to_add:
                creator(el)
            else:
                compartment.append(mapping[el])

        #log.debug('elements order in model: %s' % [f.name for f in elements])
        #log.debug('elements order in diagram: %s' % [f.subject.name for f in compartment])
        assert tuple([f.subject for f in compartment]) == tuple(elements)

        self.request_update()


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        NamedItem.on_subject_notify(self, pspec, ('isAbstract',) + notifiers)
        # Create already existing attributes and operations:
        if self.subject:
            self.on_subject_notify__isAbstract(self.subject)
        self.request_update()

    def on_subject_notify__isAbstract(self, subject, pspec=None):
        self._name.font = subject.isAbstract \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()


    def pre_update_compartment(self, context):
        """
        Calculate minimal size, which is based on comparment sizes.
        """
        super(ClassifierItem, self).pre_update(context)

        for comp in self._compartments:
            comp.pre_update(context)

        # take current minimal size into account
        sizes = [ (self.min_width, 0) ]
        sizes.extend(comp.get_size() for comp in self._compartments)

        self.min_width = max(size[0] for size in sizes)
        self.min_height = sum(size[1] for size in sizes)


    def pre_update_compartment_icon(self, context):
        self.pre_update_compartment(context)

    def pre_update_icon(self, context):
        super(ClassifierItem, self).pre_update(context)

    def update_compartment(self, context):
        """
        Update state for box-style presentation.
        """
        super(ClassifierItem, self).update(context)


    def update_compartment_icon(self, context):
        """
        Update state for box-style w/ small icon.
        """
        super(ClassifierItem, self).update(context)

    def update_icon(self, context):
        """
        Update state for icon-only presentation.
        """
        super(ClassifierItem, self).update(context)

    def get_icon_pos(self):
        """
        Get icon position.
        """
        return self.width - self.ICON_MARGIN_X - self.ICON_WIDTH, \
            self.ICON_MARGIN_Y


    def draw_compartment(self, context):
        super(ClassifierItem, self).draw(context)

        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        # make room for name, stereotype, etc.
        y = self._header_size[1]
        cr.translate(0, y)

        if self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            width = self.width - self.ICON_WIDTH
        else:
            width = self.width

        # draw compartments
        for comp in self._compartments:
            if not comp.visible:
                continue
            cr.save()
            cr.move_to(0, 0)
            cr.line_to(self.width, 0)
            cr.stroke()
            try:
                comp.draw(context)
            finally:
                cr.restore()
            cr.translate(0, comp.height)


    def item_at(self, x, y):
        """
        Find the composite item (attribute or operation) for the classifier.
        """

        if self.drawing_style not in (ClassifierItem.DRAW_COMPARTMENT, ClassifierItem.DRAW_COMPARTMENT_ICON):
            return self

        name_comp_height = self._name.bounds.height
        # Edit is in name compartment -> edit name
        if y < name_comp_height:
            return self

        padding = self.style.compartment_padding
        vspacing = self.style.compartment_vspacing
        
        # place offset at top of first comparement
        y -= name_comp_height
        y += vspacing / 2.0
        for comp in self.compartments:
            if not comp.visible:
                continue
            item = comp.item_at(x, y)
            if item:
                return item
            y -= comp.height
        return None

# vim:sw=4:et
