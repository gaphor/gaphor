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
from classifier import ClassifierItem
from feature import FeatureItem
from attribute import AttributeItem
from operation import OperationItem

class Compartment(object):
    """Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.visible = True
        self.items = []
        self.separator = diacanvas.shape.Path()
        self.separator.set_line_width(2.0)
        self.sep_y = 0

    def save(self, save_func):
        #log.debug('Compartment.save: %s' % self.items)
        for item in self.items:
            save_func(None, item)

    # Loading is done directly in the FeatureItem

    def create(self, feature):
        assert isinstance(feature, UML.Feature)
        for f in self.items:
            if f.subject is feature:
                return
        if isinstance(feature, UML.Property):
            if feature.association:
                return
            item = AttributeItem()
        elif isinstance(feature, UML.Operation):
            item = OperationItem()
        else:
            raise ValueError, 'Unsupported class type for compartment: %s' % type(feature).__name__
        item.set_property('subject', feature)

        self.owner.add(item)
        self.owner.request_update()
        item.focus()

    def append(self, item):
        if item not in self.items:
            self.items.append(item)

    def remove(self, feature):
        for f in self.items:
            if f.subject is feature:
                self.owner.remove(f)
                return
        self.owner.request_update()

    def pre_update(self, width, height, affine):
        if self.visible:
            self.sep_y = height
            height += ClassItem.COMP_MARGIN_Y
            for f in self.items:
                #log.debug(f)
                layout = f.get_property('layout')
                w, h = layout.get_pixel_size()
                if affine:
                    a = f.get_property('affine')
                    a = (a[0], a[1], a[2], a[3], ClassItem.COMP_MARGIN_X, height)
                    f.set(affine=a, height=h, width=w, visible=True)
                height += h
                width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)
            height += ClassItem.COMP_MARGIN_Y
        else:
            for f in self.items:
                f.set_property('visible', False)
        return width, height

    def update(self, width, affine):
        if self.visible:
            for f in self.items:
                self.owner.update_child(f, affine)
            self.separator.line(((0, self.sep_y), (width, self.sep_y)))


class ClassItem(ClassifierItem):
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

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=100)
        self._attributes = Compartment('attributes', self)
        self._operations = Compartment('operations', self)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'show-attributes')
        self.save_property(save_func, 'show-operations')
        ClassifierItem.save(self, save_func)
        #for comp in (self._attributes, self._operations):
            #comp.save(save_func)

    def postload(self):
        ClassifierItem.postload(self)
        #self.on_subject_notify__ownedAttribute(self.subject)
        #self.on_subject_notify__ownedOperation(self.subject)
        for f in self.subject.ownedAttribute:
            if not f.association:
                self._attributes.create(f)
        for f in self.subject.ownedOperation:
            self._operations.create(f)

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
            ClassifierItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'show-attributes':
            return self._attributes.visible
        elif pspec.name == 'show-operations':
            return self._operations.visible
        return ClassifierItem.do_get_property(self, pspec)

    def has_capability(self, capability):
        log.debug('has_capability: %s' % capability)
        if capability == 'show-attributes':
            return self._attributes.visible
        elif capability == 'show-operations':
            return self._operations.visible
        return ClassifierItem.has_capability(self, capability)

    def on_subject_notify(self, pspec, notifiers=()):
        ClassifierItem.on_subject_notify(self, pspec, ('ownedAttribute', 'ownedOperation'))
        # Create already existing attributes and operations:
        if self.subject:
            for f in self.subject.ownedAttribute:
                if not f.association:
                    self._attributes.create(f)
            for f in self.subject.ownedOperation:
                self._operations.create(f)
        self.request_update()

    def sync_owned_features(self, features, compartment):
        """Common function for on_subject_notify__ownedAttribute() and
        on_subject_notify__ownedOperation().
        """
        featlen = len(features)
        mylen = len(compartment.items)
        myfeat = map(getattr, compartment.items,
                      ['subject'] * len(compartment.items))
        if featlen > mylen: # item added
            for a in features:
                if a not in myfeat:
                    compartment.create(a)
                    break
        elif featlen < mylen: # item removed
            for a in myfeat:
                if a not in features:
                    compartment.remove(a)
                    break

    def on_subject_notify__ownedAttribute(self, subject, pspec=None):
        # Note: This method is also called in postload()
        #log.debug('on_subject_notify__ownedAttribute')
        # Filter attributes that are connected to an association:
        attr = []
        for a in subject.ownedAttribute:
            if not a.association:
                attr.append(a)
        self.sync_owned_features(attr, self._attributes)
        #self.compare_owned_features(subject.ownedAttribute, self._attributes)

    def on_subject_notify__ownedOperation(self, subject, pspec=None):
        # Note: This method is also called in postload()
        #log.debug('on_subject_notify__ownedOperation')
        self.sync_owned_features(subject.ownedOperation, self._operations)

    def on_update(self, affine):
        """Overrides update callback. If affine is None, it is called just for
        updating the item width and height."""

        width = 0
        height = ClassItem.HEAD_MARGIN_Y

        # TODO: update stereotype

        # Update class name
        w, name_height = self.get_name_size()
        height += name_height
        name_y = height / 2
        #self.update_name(x=0, y=self.height / 2,
        #                 width=self.width, height=h)
        #if affine:
        #    a = self._name.get_property('affine')
        #    a = (a[0], a[1], a[2], a[3], a[4], height / 2)
        #    self._name.set(affine=a, height=h)
        
        height += ClassItem.HEAD_MARGIN_Y
        width = w + ClassItem.HEAD_MARGIN_X

        for comp in (self._attributes, self._operations):
            width, height = comp.pre_update(width, height, affine)

        self.set(min_width=width, min_height=height)

        #if affine:
        width = max(width, self.width)
        height = max(height, self.height)

        # We know the width of all text components and set it:
        # Note: here the upadte flag is set for all sub-items (again)!
        #    self._name.set_property('width', width)
        self.update_name(x=0, y=name_y, width=width, height=name_height)

        for comp in (self._attributes, self._operations):
            comp.update(width, affine)

        ClassifierItem.on_update(self, affine)

        self._border.rectangle((0,0),(width, height))
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in ClassifierItem.on_shape_iter(self):
            yield s
        if self._attributes.visible:
            yield self._attributes.separator
        if self._operations.visible:
            yield self._operations.separator

    # Groupable

    def on_groupable_add(self, item):
        """Add an attribute or operation."""
        #if isinstance(item.subject, UML.Property):
        if isinstance(item, AttributeItem):
            #log.debug('Adding attribute %s' % item)
            self._attributes.append(item)
        #elif isinstance(item.subject, UML.Operation):
        elif isinstance(item, OperationItem):
            #log.debug('Adding operation %s' % item)
            self._operations.append(item)
        else:
            log.warning('feature %s is not a Feature' % item)
            return 0
        self.request_update()
        return 1

    def on_groupable_remove(self, item):
        """Remove a feature subitem."""
        if item in self._attributes.items:
            self._attributes.items.remove(item)
        elif item in self._operations.items:
            self._operations.items.remove(item)
        else:
            log.warning('feature %s not found in feature list' % item)
            return 0
        self.request_update()
        #log.debug('Feature removed: %s' % item)
        return 1

    def on_groupable_iter(self):
        #log.debug('on_groupable_iter')
        for i in ClassifierItem.on_groupable_iter(self):
            yield i
        for i in self._attributes.items:
            #log.debug('on_groupable_iter (attr): %s' % i)
            yield i
        for i in self._operations.items:
            #log.debug('on_groupable_iter (oper): %s' % i)
            yield i

    def on_groupable_length(self):
        return ClassifierItem.on_groupable_length(self) \
               + len(self._attributes.items) + len(self._operations.items)

    def on_groupable_pos(self, item):
        #if item == self._name:
        #    return 0
        if item in self._attributes.items:
            return self._attributes.items.index(item)
        elif item in self._operations.items:
            return len(self._attributes.items) + self._operations.items.index(item)
        else:
            return -1

    def __on_subject_update(self, name, old_value, new_value):
        """Update self when the subject changes."""
        if name == '__unlink__':
            for f in self.__features:
                f.set_subject(None)
            #assert len(self.__features) == 0, '%d features still exist' % len(self.__features)
            ClassifierItem.on_subject_update(self, name, old_value, new_value)
        elif name == 'name':
            self._name.set(text=self.subject.name)
        elif name == 'feature' and (self.canvas and not self.canvas.in_undo):
            # Only hande the feature if we're part of a diagram
            #log.debug('on_subject_update(%s, %s)' % (old_value, new_value))
            if old_value == 'add':
                self._add_feature(new_value)
            elif old_value == 'remove':
                self._remove_feature(new_value)


gobject.type_register(ClassItem)
