"""ClassItem diagram item
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
from attribute import AttributeItem
from operation import OperationItem

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
            height += ClassItem.COMP_MARGIN_Y
            for f in self:
                w, h = f.get_size(update=True)
                #log.debug('feature: %f, %f' % (w, h))
                f.set_pos(ClassItem.COMP_MARGIN_X, height)
                f.set_property('visible', True)
                height += h
                width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)
            height += ClassItem.COMP_MARGIN_Y
        else:
            for f in self:
                f.set_property('visible', False)
        return width, height

    def update(self, width, affine):
        if self.visible:
            for f in self:
                self.owner.update_child(f, affine)
            self.separator.line(((0, self.sep_y), (width, self.sep_y)))

        
class ClassItem(NamedItem, diacanvas.CanvasGroupable):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments (Compartment): one for
    attributes and one for operations. To add and remove such features
    the ClassItem implements the CanvasGroupable interface.
    Items can be added by callling class.add() and class.remove().
    This is used to handle CanvasItems, not UML objects!
    """
    __gproperties__ = {
        'show-attributes': (gobject.TYPE_BOOLEAN, 'show attributes',
                            '',
                            1, gobject.PARAM_READWRITE),
        'show-operations': (gobject.TYPE_BOOLEAN, 'show operations',
                            '',
                            1, gobject.PARAM_READWRITE),
    }
    HEAD_MARGIN_X=30
    HEAD_MARGIN_Y=10
    COMP_MARGIN_X=5
    COMP_MARGIN_Y=5

    FONT_STEREOTYPE='sans 10'
    FONT_ABSTRACT='sans bold italic 10'
    FROM_FONT='sans 8'

    stereotype_list = []
    popup_menu = NamedItem.popup_menu + (
        'Fold',
        'separator',
        'AbstractClass',
        'Stereotype', stereotype_list,
        'separator',
        'CreateAttribute',
        'CreateOperation',
        'separator',
        'ShowAttributes',
        'ShowOperations',
        '<ClassPopupSlot>'
    )

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._attributes = Compartment('attributes', self)
        self._operations = Compartment('operations', self)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

        self.has_stereotype = False
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(pango.FontDescription(self.FONT_STEREOTYPE))
        self._stereotype.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)
        #self._stereotype.set_text(STEREOTYPE_OPEN + 'stereotype' + STEREOTYPE_CLOSE)

        self._from = diacanvas.shape.Text()
        self._from.set_font_description(pango.FontDescription(ClassItem.FROM_FONT))
        self._from.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._from.set_markup(False)

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'show-attributes')
        self.save_property(save_func, 'show-operations')
        NamedItem.save(self, save_func)

    def postload(self):
        NamedItem.postload(self)
        self.sync_attributes()
        self.sync_operations()
        self.on_subject_notify__isAbstract(self.subject)

    def get_popup_menu(self):
        """In the popup menu a submenu is created with Stereotypes than can be
        applied to this classifier (Class, Interface).
        If the class itself is a metaclass, an option is added to check if the class
        exists.
        """
        subject = self.subject
        stereotype_list = self.stereotype_list
        stereotype_list[:] = []
        if isinstance(subject, UML.Class) and subject.extension:
            # Add an action that can be used to check if the metaclass is an
            # existing metaclass
            pass
        else:
            from itemactions import ApplyStereotypeAction, register_action
            NamedElement = UML.NamedElement
            Class = UML.Class

            # Find classes that are superclasses of our subject
            _mro = filter(lambda e:issubclass(e, NamedElement), type(self.subject).__mro__)
            # Find out their names
            names = map(getattr, _mro, ['__name__'] * len(_mro))
            # Find stereotypes that extend out metaclass
            classes = self._subject._factory.select(lambda e: e.isKindOf(Class) and e.name in names)

            for class_ in classes:
                for extension in class_.extension:
                    stereotype = extension.ownedEnd.type
                    stereotype_action = ApplyStereotypeAction(stereotype)
                    register_action(stereotype_action, 'ItemFocus')
                    stereotype_list.append(stereotype_action.id)
        return NamedItem.get_popup_menu(self)

    def do_set_property(self, pspec, value):
        if pspec.name == 'show-attributes':
            self.preserve_property('show-attributes')
            self._attributes.visible = value
            self.request_update()
        elif pspec.name == 'show-operations':
            self.preserve_property('show-operations')
            self._operations.visible = value
            self.request_update()
        else:
            NamedItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'show-attributes':
            return self._attributes.visible
        elif pspec.name == 'show-operations':
            return self._operations.visible
        return NamedItem.do_get_property(self, pspec)

    def _create_attribute(self, attribute):
        """Create a new attribute item.
        """
        new = AttributeItem()
        new.subject = attribute
        self.add(new)

    def _create_operation(self, operation):
        """Create a new operation item.
        """
        new = OperationItem()
        new.subject = operation
        self.add(new)
        
    def sync_uml_elements(self, elements, compartment, creator=None):
        """Common function for on_subject_notify__ownedAttribute() and
        on_subject_notify__ownedOperation().
        - elements: the list of attributes or operations in the model
        - compartment: our local representation
        - creator: factory method for creating new attr. or oper.'s
        """
        # extract the UML elements from the compartment
        local_elements = [f.subject for f in compartment]

        # map local element with compartment element
        mapping = dict(zip(local_elements, compartment))

        to_add = [el for el in elements if el not in local_elements]

        print 'sync_elems:', local_elements, to_add

        # sync local elements with elements
        del compartment[:]

        for el in elements:
            if el in to_add:
                print 'sync_elems: creating', el
                creator(el)
            else:
                compartment.append(mapping[el])

        #log.debug('elements order in model: %s' % [f.name for f in elements])
        #log.debug('elements order in diagram: %s' % [f.subject.name for f in compartment])
        assert tuple([f.subject for f in compartment]) == tuple(elements)

        self.request_update()
            

    def sync_attributes(self):
        """Sync the contents of the attributes compartment with the data
        in self.subject.
        """
        owned_attributes = [a for a in self.subject.ownedAttribute if not a.association]
        self.sync_uml_elements(owned_attributes, self._attributes,
                           self._create_attribute)

    def sync_operations(self):
        """Sync the contents of the operations compartment with the data
        in self.subject.
        """
        self.sync_uml_elements(self.subject.ownedOperation, self._operations,
                           self._create_operation)

    def update_stereotype(self):
        """Update the stereotype definitions on this class.

        Note: This method is also called from ExtensionItem.confirm_connect_handle
        """
        subject = self.subject
        applied_stereotype = self.subject.appliedStereotype
        if applied_stereotype:
            # Return a nice name to display as stereotype:
            # make first character lowercase unless the second character is uppercase.
            s = ', '.join([s and len(s) > 1 and s[1].isupper() and s \
                           or s and s[0].lower() + s[1:] \
                           or str(s) for s in map(getattr, applied_stereotype, ['name'] * len(applied_stereotype))])
            # Phew!
            self._stereotype.set_text(STEREOTYPE_OPEN + s + STEREOTYPE_CLOSE)
            self.has_stereotype = True
        elif isinstance(subject, UML.Stereotype):
            self._stereotype.set_text(STEREOTYPE_OPEN + 'stereotype' + STEREOTYPE_CLOSE)
            self.has_stereotype = True
        elif isinstance(subject, UML.Interface):
            self._stereotype.set_text(STEREOTYPE_OPEN + 'interface' + STEREOTYPE_CLOSE)
            self.has_stereotype = True
        elif isinstance(subject, UML.Class) and subject.extension:
            self._stereotype.set_text(STEREOTYPE_OPEN + 'metaclass' + STEREOTYPE_CLOSE)
            self.has_stereotype = True
        else:
            self.has_stereotype = False
        self.request_update()

    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        NamedItem.on_subject_notify(self, pspec,
                                    ('ownedAttribute', 'ownedOperation',
                                     'namespace', 'namespace.name',
                                     'isAbstract', 'appliedStereotype'))
        # Create already existing attributes and operations:
        if self.subject:
            self.sync_attributes()
            self.sync_operations()
            self.on_subject_notify__namespace(self.subject)
            self.on_subject_notify__isAbstract(self.subject)
            self.update_stereotype()
        self.request_update()

    def on_subject_notify__ownedAttribute(self, subject, pspec=None):
        """Called when the ownedAttribute property of our subject changes.
        """
        log.debug('on_subject_notify__ownedAttribute')
        # Filter attributes that are connected to an association:
        self.sync_attributes()

    def on_subject_notify__ownedOperation(self, subject, pspec=None):
        """Called when the ownedOperation property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedOperation')
        self.sync_operations()

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

    def on_update(self, affine):
        """Overrides update callback.
        """
        has_stereotype = self.has_stereotype

        width = 0
        height = ClassItem.HEAD_MARGIN_Y

        #self.sync_attributes()
        #self.sync_operations()

        compartments = (self._attributes, self._operations)

        if has_stereotype:
            st_width, st_height = self._stereotype.to_pango_layout(True).get_pixel_size()
            width = st_width + ClassItem.HEAD_MARGIN_X/2
            st_y = height = height / 2
            height += st_height

        # Update class name
        name_width, name_height = self.get_name_size()
        name_y = height
        height += name_height
        
        height += ClassItem.HEAD_MARGIN_Y
        width = max(width, name_width + ClassItem.HEAD_MARGIN_X)

        for comp in compartments: width, height = comp.pre_update(width, height, affine)

        self.set(min_width=width, min_height=height)

        #if affine:
        width = max(width, self.width)
        height = max(height, self.height)

        # TODO: update stereotype
        if has_stereotype:
            self._stereotype.set_pos((0, st_y))
            self._stereotype.set_max_width(width)
            self._stereotype.set_max_height(st_height)

        # We know the width of all text components and set it:
        # Note: here the upadte flag is set for all sub-items (again)!
        #    self._name.set_property('width', width)
        self.update_name(x=0, y=name_y, width=width, height=name_height)

        self._from.set_pos((0, name_y + name_height-2))
        self._from.set_max_width(width)
        self._from.set_max_height(name_height)

        for comp in compartments:
            comp.update(width, affine)

        NamedItem.on_update(self, affine)

        self._border.rectangle((0,0),(width, height))
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in NamedItem.on_shape_iter(self):
            yield s
        if self.has_stereotype:
            yield self._stereotype
        yield self._from
        if self._attributes.visible:
            yield self._attributes.separator
        if self._operations.visible:
            yield self._operations.separator

    # Groupable

    def on_groupable_add(self, item):
        """Add an attribute or operation.
        """
        #if isinstance(item.subject, UML.Property):
        if isinstance(item, AttributeItem):
            # TODO: check if property not already in attribute list
            if not self._attributes.has_item(item):
                log.debug('Adding attribute %s' % item)
                self._attributes.append(item)
                item.set_child_of(self)
        #elif isinstance(item.subject, UML.Operation):
        elif isinstance(item, OperationItem):
            #log.debug('Adding operation %s' % item)
            if not self._operations.has_item(item):
                self._operations.append(item)
                item.set_child_of(self)
        else:
            log.warning('feature %s is not a Feature' % item)
            return 0
        self.request_update()
        return 1

    def on_groupable_remove(self, item):
        """Remove a feature subitem.
        """
        if item in self._attributes:
            print 'remove attr:', item
            self._attributes.remove(item)
            item.set_child_of(None)
        elif item in self._operations:
            self._operations.remove(item)
            item.set_child_of(None)
        else:
            log.warning('feature %s not found in feature list' % item)
            return 0
        self.request_update()
        #log.debug('Feature removed: %s' % item)
        return 1

    def on_groupable_iter(self):
        for i in self._attributes:
            yield i
        for i in self._operations:
            yield i

initialize_item(ClassItem, UML.Class)
