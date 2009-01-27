"""
Classifier diagram item.
"""

from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.classes.feature import SlotItem, StereotypeNameItem

import font

class Compartment(list):
    """
    Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner, id=None):
        self.name = name
        self.owner = owner
        self.id = id
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

    def post_update(self, context):
        for item in self:
            item.post_update(context)

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
    Abstract class for visualization of classifiers having compartments
    like class, interface, component.

    Classifier item has ability to display stereotypes attributes in
    separate compartment per stereotype, which attributes has been changed.

    Classifier item has three drawing styles (changed with
    `ClassifierItem.drawing_style` property)

     - the comparttment view - often used by classes
     - a compartment view, but with a little stereotype icon in the right corner
     - an icon - used by actor and interface items

    Methods pre_update/post_update/draw are defined to support drawing
    styles. Appropriate methods are called depending on drawing style.
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
        self.add_watch(UML.Classifier.isAbstract, self.on_classifier_is_abstract)
        self.add_watch(UML.Element.appliedStereotype, self.on_stereotype_change)
        self.add_watch(UML.InstanceSpecification.slot, self.on_stereotype_attr_change)
        self._name.font = font.FONT_NAME


    def on_stereotype_change(self, event):
        if event and event.element is self.subject \
                and self._show_stereotypes_attrs:

            if isinstance(event, UML.event.AssociationAddEvent):
                self._create_stereotype_compartment(event.new_value)
            elif isinstance(event, UML.event.AssociationDeleteEvent):
                self._remove_stereotype_compartment(event.old_value)


    def _find_stereotype_compartment(self, obj):
        for comp in self._compartments:
            if comp.id is obj:
                return comp


    def on_stereotype_attr_change(self, event):
        if event and event.element in self.subject.appliedStereotype \
                and self._show_stereotypes_attrs:

            comp = self._find_stereotype_compartment(event.element)
            if not comp:
                log.debug('No compartment found for %s' % event.element)
                return

            if isinstance(event, (UML.event.AssociationAddEvent, UML.event.AssociationDeleteEvent)):
                self._update_stereotype_compartment(comp, event.element)

            self.request_update()


    def _create_stereotype_compartment(self, obj):
        c = Compartment(obj.classifier[0].name, self, obj)
        item = StereotypeNameItem()
        item.subject = obj.classifier[0]
        c.append(item)
        self._update_stereotype_compartment(c, obj)
        self._compartments.append(c)
        self.request_update()


    def _remove_stereotype_compartment(self, obj):
        comp = self._find_stereotype_compartment(obj)
        if comp:
            self._compartments.remove(comp)
            self.request_update()


    def _update_stereotype_compartment(self, comp, obj):
        del comp[1:]
        for slot in obj.slot:
            item = SlotItem()
            item.subject = slot
            comp.append(item)
        comp.visible = len(obj.slot) > 0


    def update_stereotypes_attrs(self):
        """
        Display or hide stereotypes attributes.
        
        New compartment is created for every stereotype having attributes
        redefined.
        """
        # remove all stereotype compartments first
        for comp in self._compartments:
            if isinstance(comp.id, UML.InstanceSpecification):
                self._compartments.remove(comp)
        if self._show_stereotypes_attrs:
            for obj in self.subject.appliedStereotype:
                self._create_stereotype_compartment(obj)
            log.debug('Showing stereotypes attributes enabled')
        else:
            log.debug('Showing stereotypes attributes disabled')


    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'drawing-style')
        NamedItem.save(self, save_func)


    def postload(self):
        NamedItem.postload(self)
        self.on_classifier_is_abstract(None)


    @observed
    def set_drawing_style(self, style):
        """
        Set the drawing style for this classifier: DRAW_COMPARTMENT,
        DRAW_COMPARTMENT_ICON or DRAW_ICON.
        """
        if style != self._drawing_style:
            self._drawing_style = style
            self.request_update()
#            if self.canvas:
#                request_resolve = self.canvas.solver.request_resolve
#                for h in self._handles: 
#                    request_resolve(h.x)
#                    request_resolve(h.y)

        if self._drawing_style == self.DRAW_COMPARTMENT:
            self.draw       = self.draw_compartment
            self.pre_update = self.pre_update_compartment
            self.post_update = self.post_update_compartment

        elif self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.draw       = self.draw_compartment_icon
            self.pre_update = self.pre_update_compartment_icon
            self.post_update     = self.post_update_compartment_icon

        elif self._drawing_style == self.DRAW_ICON:
            self.draw       = self.draw_icon
            self.pre_update = self.pre_update_icon
            self.post_update     = self.post_update_icon


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


    def on_classifier_is_abstract(self, event):
        self._name.font = (self.subject and self.subject.isAbstract) \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()


    def pre_update_compartment_icon(self, context):
        self.pre_update_compartment(context)
        # icon width plus right margin
        self.min_width = max(self.min_width,
                self._header_size[0] + self.ICON_WIDTH + 10)

    def pre_update_icon(self, context):
        super(ClassifierItem, self).pre_update(context)

    def pre_update_compartment(self, context):
        """
        Update state for box-style presentation.

        Calculate minimal size, which is based on header and comparments
        sizes.
        """
        super(ClassifierItem, self).pre_update(context)

        for comp in self._compartments:
            comp.pre_update(context)

        sizes = [comp.get_size() for comp in self._compartments]
        sizes.append((self.min_width, self._header_size[1]))

        self.min_width = max(size[0] for size in sizes)
        h = sum(size[1] for size in sizes)
        self.min_height = max(self.style.min_size[1], h)


    def post_update_compartment_icon(self, context):
        """
        Update state for box-style w/ small icon.
        """
        super(ClassifierItem, self).post_update(context)

    def post_update_icon(self, context):
        """
        Update state for icon-only presentation.
        """
        super(ClassifierItem, self).post_update(context)

    def post_update_compartment(self, context):
        super(ClassifierItem, self).post_update(context)

        assert self.width >= self.min_width, 'failed %s >= %s' % (self.width, self.min_width)
        assert self.height >= self.min_height, 'failed %s >= %s' % (self.height, self.min_height)


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

        # draw compartments and stereotype compartments
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
        Find the composite item (attribute or operation) for the
        classifier.
        """

        if self.drawing_style not in (self.DRAW_COMPARTMENT, self.DRAW_COMPARTMENT_ICON):
            return self

        header_height = self._header_size[1]

        compartments = [ comp for comp in self.compartments if comp.visible]

        # Edit is in name compartment -> edit name
        if y < header_height or not len(compartments):
            return self

        padding = self.style.compartment_padding
        vspacing = self.style.compartment_vspacing
        
        # place offset at top of first comparement
        y -= header_height
        y += vspacing / 2.0
        for comp in compartments:
            item = comp.item_at(x, y)
            if item:
                return item
            y -= comp.height
        return None

# vim:sw=4:et
