"""ClassifierItem diagram item
"""
# vim:sw=4:et

# TODO: make loading of features work (adjust on_groupable_add)
#       probably best to do is subclass Feature in OperationItem and A.Item

from __future__ import generators

import gobject
import pango
import diacanvas

import gaphor.UML as UML
from gaphor.diagram import initialize_item
from gaphor.i18n import _

from nameditem import NamedItem
from feature import FeatureItem

STEREOTYPE_OPEN = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class Compartment(list):
    """Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.visible = True
        self.separator = diacanvas.shape.Path()
        self.separator.set_line_width(2.0)
        self.sep_y = 0

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

    def pre_update(self, width, height, affine):
        """Calculate the size of the feates in this compartment.
        """
        if self.visible:
            self.sep_y = height
            height += ClassifierItem.COMP_MARGIN_Y
            for f in self:
                w, h = f.get_size(update=True)
                #log.debug('feature: %f, %f' % (w, h))
                f.set_pos(ClassifierItem.COMP_MARGIN_X, height)
                f.set_property('visible', True)
                height += h
                width = max(width, w + 2 * ClassifierItem.COMP_MARGIN_X)
            height += ClassifierItem.COMP_MARGIN_Y
        else:
            for f in self:
                f.set_property('visible', False)
        return width, height

    def update(self, width, affine):
        if self.visible:
            for f in self:
                self.owner.update_child(f, affine)
            self.separator.line(((0, self.sep_y), (width, self.sep_y)))

        
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
     - update_compartment (the standard box-style)
     - update_compartment_icon (box-style with small icon (see ComponentItem))
     - update_compartment_common (update parts used in both methods)
     - update_icon (does nothing by default, an impl. should be provided by
                    subclasses (see ActorItem))
    """

    # Draw the famous box style
    DRAW_COMPARTMENT = 0
    # Draw compartment with little icon in upper right corner
    DRAW_COMPARTMENT_ICON = 1
    # Draw as icon
    DRAW_ICON = 2

    __gproperties__ = {
        'drawing-style':   (gobject.TYPE_INT, 'Drawing style',
                            'set the drawing style for the classifier',
                            0, 2, 0, gobject.PARAM_READWRITE),
    }
    HEAD_MARGIN_X = 30
    HEAD_MARGIN_Y = 10
    COMP_MARGIN_X = 5 
    COMP_MARGIN_Y = 5
    # Default size for small icons
    ICON_WIDTH    = 15
    ICON_HEIGHT   = 25
    ICON_MARGIN_X = 10
    ICON_MARGIN_Y = 10

    FONT_STEREOTYPE='sans 10'
    FONT_ABSTRACT='sans bold italic 10'
    FROM_FONT='sans 8'

    stereotype_list = []

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._compartments = []
        self._drawing_style = ClassifierItem.DRAW_COMPARTMENT

        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

        self._has_stereotype = False
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(pango.FontDescription(self.FONT_STEREOTYPE))
        self._stereotype.set_alignment(pango.ALIGN_CENTER)
        self._stereotype.set_markup(False)

        self._from = diacanvas.shape.Text()
        self._from.set_font_description(pango.FontDescription(ClassifierItem.FROM_FONT))
        self._from.set_alignment(pango.ALIGN_CENTER)
        self._from.set_markup(False)

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'drawing-style')
        NamedItem.save(self, save_func)

    def postload(self):
        NamedItem.postload(self)
        self.on_subject_notify__isAbstract(self.subject)

    def do_set_property(self, pspec, value):
        if pspec.name == 'drawing-style':
            self.set_drawing_style(value)
        else:
            NamedItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'drawing-style':
            return self._drawing_style
        return NamedItem.do_get_property(self, pspec)

    def set_drawing_style(self, style):
        """Set the drawing style for this classifier: DRAW_COMPARTMENT,
        DRAW_COMPARTMENT_ICON or DRAW_ICON.
        """
        if style != self._drawing_style:
            self.preserve_property('drawing-style')
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

        #log.debug('elements order in model: %s' % [f.name for f in elements])
        #log.debug('elements order in diagram: %s' % [f.subject.name for f in compartment])
        assert tuple([f.subject for f in compartment]) == tuple(elements)

        self.request_update()

    def set_stereotype(self, text=None):
        """Set the stereotype text for the diagram item.
        The text, not a Stereotype object.
        @text: text to set.
        """
        if text:
            self._stereotype.set_text(STEREOTYPE_OPEN + text + STEREOTYPE_CLOSE)
            self._has_stereotype = True
        else:
            self._has_stereotype = False
        self.request_update()

    def update_stereotype(self):
        """Update the stereotype definitions (text) on this class.

        Note: This method is also called from
        ExtensionItem.confirm_connect_handle
        """
        subject = self.subject
        applied_stereotype = subject.appliedStereotype
        if applied_stereotype:
            # Return a nice name to display as stereotype:
            # make first character lowercase unless the second character is uppercase.
            s = ', '.join([s and len(s) > 1 and s[1].isupper() and s \
                           or s and s[0].lower() + s[1:] \
                           or str(s) for s in map(getattr, applied_stereotype, ['name'] * len(applied_stereotype))])
            # Phew!
            self.set_stereotype(s)
            return True
        else:
            self.set_stereotype(None)

    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        NamedItem.on_subject_notify(self, pspec,
                                    ('namespace', 'namespace.name',
                                     'isAbstract', 'appliedStereotype') + notifiers)
        # Create already existing attributes and operations:
        if self.subject:
            self.on_subject_notify__namespace(self.subject)
            self.on_subject_notify__isAbstract(self.subject)
            self.update_stereotype()
        self.request_update()

    def on_subject_notify__namespace(self, subject, pspec=None):
        """Add a line '(from ...)' to the class item if subject's namespace
        is not the same as the namespace of this diagram.
        """
        #print 'on_subject_notify__namespace', self, subject
        if self.subject and self.subject.namespace and self.canvas and \
           self.canvas.diagram.namespace is not self.subject.namespace:
            self._from.set_text(_('(from %s)') % self.subject.namespace.name)
        else:
            self._from.set_text('')
        self.request_update()

    def on_subject_notify__namespace_name(self, subject, pspec=None):
        """Change the '(from ...)' line if the namespace's name changes.
        """
        print 'on_subject_notify__namespace_name', self, subject
        self.on_subject_notify__namespace(subject, pspec)

    def on_subject_notify__isAbstract(self, subject, pspec=None):
        subject = self.subject
        if subject.isAbstract:
            self._name.set_font_description(pango.FontDescription(self.FONT_ABSTRACT))
        else:
            self._name.set_font_description(pango.FontDescription(self.FONT))
        self.request_update()

    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
        if self.subject:
            self.update_stereotype()

    def update_compartment_common(self, affine, width, height):
        """Update parts that are common for update_compartment() and
        update_compartment_icon().

        @affine:
        @width: Height calculated before this function was called.
        @height: Width
        @return: (width, height) newly calculated size.
        """
        # Update class name
        name_width, name_height = self.get_name_size()
        name_y = height
        height += name_height
        
        height += ClassifierItem.HEAD_MARGIN_Y
        width = max(width, name_width + ClassifierItem.HEAD_MARGIN_X)

        compartments = self._compartments

        for comp in compartments: width, height = comp.pre_update(width, height, affine)

        self.set(min_width=width, min_height=height)

        width = max(width, self.width)
        height = max(height, self.height)

        # We know the width of all text components and set it:
        # Note: here the upadte flag is set for all sub-items (again)!
        #    self._name.set_property('width', width)
        self.update_name(x=0, y=name_y, width=width, height=name_height)

        self._from.set_pos((0, name_y + name_height-2))
        self._from.set_max_width(width)
        self._from.set_max_height(name_height)

        for comp in compartments:
            comp.update(width, affine)

        self._border.rectangle((0,0),(width, height))

        return width, height

    def update_compartment(self, affine):
        """Update state so it can draw itself with the box style.
        """
        has_stereotype = self._has_stereotype

        width = 0
        height = ClassifierItem.HEAD_MARGIN_Y

        if has_stereotype:
            st_width, st_height = self._stereotype.to_pango_layout(True).get_pixel_size()
            width = st_width + ClassifierItem.HEAD_MARGIN_X/2
            st_y = height = height / 2
            height += st_height

        width, height = self.update_compartment_common(affine, width, height)

        if has_stereotype:
            self._stereotype.set_pos((0, st_y))
            self._stereotype.set_max_width(width)
            self._stereotype.set_max_height(st_height)


    def update_compartment_icon(self, affine):
        """Update state for box-style w/ small icon.
        """
        self.update_compartment_common(affine, self.ICON_WIDTH, self.ICON_HEIGHT + self.ICON_MARGIN_Y)

    def update_icon(self, affine):
        """Update state to draw as one bug icon.
        """
        pass

    def on_update(self, affine):
        """Overrides update callback.
        """
        if self._drawing_style == self.DRAW_COMPARTMENT:
            self.update_compartment(affine)
        elif self._drawing_style == self.DRAW_COMPARTMENT_ICON:
            self.update_compartment_icon(affine)
        elif self._drawing_style == self.DRAW_ICON:
            self.update_icon(affine)
        else:
            raise Exception, "Unknown drawing style: %s" % self._drawing_style

        NamedItem.on_update(self, affine)

        self.expand_bounds(1.0)

    def on_shape_iter(self):
        if self._drawing_style in (self.DRAW_COMPARTMENT, self.DRAW_COMPARTMENT_ICON):
            yield self._border
            if self._has_stereotype and self._drawing_style == self.DRAW_COMPARTMENT:
                yield self._stereotype
            yield self._from

            for c in self._compartments:
                if c.visible:
                    yield c.separator

        for s in NamedItem.on_shape_iter(self):
            yield s

initialize_item(ClassifierItem)
