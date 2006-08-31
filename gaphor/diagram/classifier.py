"""ClassifierItem diagram item
"""
# vim:sw=4:et

# TODO: make loading of features work (adjust on_groupable_add)
#       probably best to do is subclass Feature in OperationItem and A.Item

import itertools

from gaphor import UML
from gaphor.i18n import _

from gaphor.diagram.nameditem import NamedItem, NamedItemMeta
from gaphor.diagram.feature import FeatureItem
from gaphor.diagram.align import MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT

from gaphas.util import text_center

class Compartment(list):
    """Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    MARGIN_X = 5 
    MARGIN_Y = 5

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
        """Check if the compartment already contains an item with the
        same subject as item.
        """
        s = item.subject
        local_elements = [f.subject for f in self]
        return s and s in local_elements

    def pre_update(self, context):
        cr = context.cairo
        for item in self:
            item.pre_update(context)
        if self:
            sizes = [f.get_size(True) for f in self]
            self.width = max(map(lambda p: p[0], sizes))
            self.height = sum(map(lambda p: p[1], sizes))
        self.width += 2 * self.MARGIN_X
        self.height += 2*self.MARGIN_Y

    def get_size(self):
        return self.width, self.height

    def update(self, context):
        for item in self:
            self.update(self, context)


class ClassifierItem(NamedItem):
    """This item visualizes a Class instance.

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
    # Draw the famous box style
    DRAW_COMPARTMENT = 0
    # Draw compartment with little icon in upper right corner
    DRAW_COMPARTMENT_ICON = 1
    # Draw as icon
    DRAW_ICON = 2

    # Default size for small icons
    ICON_WIDTH    = 15
    ICON_HEIGHT   = 25
    ICON_MARGIN_X = 10
    ICON_MARGIN_Y = 10

    FONT_ABSTRACT   = 'sans bold italic 10'
    FONT_FROM       = 'sans 8'

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.height = 50
        self.width = 100
        self._compartments = []
        self._drawing_style = ClassifierItem.DRAW_COMPARTMENT

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'drawing-style')
        NamedItem.save(self, save_func)

    def postload(self):
        NamedItem.postload(self)
        self.on_subject_notify__isAbstract(self.subject)

    def set_drawing_style(self, style):
        """Set the drawing style for this classifier: DRAW_COMPARTMENT,
        DRAW_COMPARTMENT_ICON or DRAW_ICON.
        """
        if style != self._drawing_style:
            #self.preserve_property('drawing-style')
            self._drawing_style = style
            self.request_update()

    drawing_style = property(lambda self: self._drawing_style, set_drawing_style)

    def create_compartment(self, name):
        """Create a new compartment. Compartments contain data such as
        attributes and operations.

        It is common to create compartments during the construction of the
        diagram item. Their visibility can be toggled by Compartment.visible.
        """
        c = Compartment(name, self)
        self._compartments.append(c)
        return c

    def sync_uml_elements(self, elements, compartment, creator=None):
        """This method synchronized a list of elements with the items
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

        #print 'sync_elems:', elements, local_elements, to_add

        # Remove no longer present elements:
        for el in [el for el in local_elements if el not in elements]:
            self.remove(mapping[el])

        # sync local elements with elements
        del compartment[:]

        for el in elements:
            if el in to_add:
                #print 'sync_elems: creating', el
                creator(el)
            else:
                compartment.append(mapping[el])

        log.debug('elements order in model: %s' % [f.name for f in elements])
        log.debug('elements order in diagram: %s' % [f.subject.name for f in compartment])
        assert tuple([f.subject for f in compartment]) == tuple(elements)

        self.request_update()


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        NamedItem.on_subject_notify(self, pspec,
                                    ('namespace', 'namespace.name',
                                     'isAbstract') + notifiers)
        # Create already existing attributes and operations:
        if self.subject:
            self.on_subject_notify__namespace(self.subject)
            self.on_subject_notify__isAbstract(self.subject)
        self.request_update()

    def on_subject_notify__namespace(self, subject, pspec=None):
        """Add a line '(from ...)' to the class item if subject's namespace
        is not the same as the namespace of this diagram.
        """
        self.request_update()

    def on_subject_notify__namespace_name(self, subject, pspec=None):
        """Change the '(from ...)' line if the namespace's name changes.
        """
        self.on_subject_notify__namespace(subject, pspec)

    def on_subject_notify__isAbstract(self, subject, pspec=None):
        self.request_update()

    def pre_update(self, context):
        for comp in self._compartments:
            comp.pre_update(context)

        if self._drawing_style == self.DRAW_COMPARTMENT:
            sizes = [comp.get_size() for comp in self._compartments]

            if sizes:
                width = max(map(lambda p: p[0], sizes)) + Compartment.MARGIN_X * 2

                height = sum(map(lambda p: p[1], sizes))
                height += len(self._compartments) * Compartment.MARGIN_Y * 2
                self.min_width = width
                self.min_height = height

    def update_compartment_icon(self, context):
        """Update state for box-style w/ small icon.
        """
        pass


    def update_icon(self, context):
        """Update state to draw as one big icon.
        """
        pass


    def get_icon_pos(self):
        """Get icon position.
        """
        return self.width - self.ICON_MARGIN_X - self.ICON_WIDTH, \
            self.ICON_MARGIN_Y

    def update(self, context):
        """Overrides update callback.
        """
        if self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.update_compartment_icon(context)
        elif self._drawing_style == self.DRAW_ICON:
            self.update_icon(context)

        NamedItem.update(self, context)

    def draw_compartment(self, context):
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)

        # draw stereotype

        # draw name

        # draw 'from ... '

        # draw compartments
        for comp in self._compartments:

            comp.draw(context)
    def draw(self, context):
        if self._drawing_style == self.DRAW_COMPARTMENT:
            self.draw_compartment(context)
        elif self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.draw_compartment(context)
            self.draw_compartment_icon(context)
        elif self._drawing_style == self.DRAW_ICON:
            self.draw_icon(context)
