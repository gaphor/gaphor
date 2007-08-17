#!/usr/bin/env python
# vim:sw=4:et
"""
Properties used to create the UML 2.0 data model.

The logic for creating and destroying connections between UML objects is
implemented in Python property classes. These classes are simply instantiated
like this:
    class Class(Element): pass
    class Comment(Element): pass
    Class.ownedComment = association('ownedComment', Comment,
                                     0, '*', 'annotatedElement')
    Comment.annotatedElement = association('annotatedElement', Element,
                                           0, '*', 'ownedComment')

Same for attributes and enumerations.

Each property type (association, attribute and enumeration) has three specific
methods:
    _get():           return the value
    _set(value):      set the value or add it to a list
    _del(value=None): delete the value. 'value' is used to tell which value
                      is to be removed (in case of associations with
                      multiplicity > 1).
    load(value):      load 'value' as the current value for this property
    save(save_func):  send the value of the property to save_func(name, value)
"""

__all__ = [ 'attribute', 'enumeration', 'association', 'derivedunion', 'redefine' ]

from zope import component
from collection import collection
from event import AttributeChangeEvent, AssociationSetEvent, \
                  AssociationAddEvent, AssociationDeleteEvent
from interfaces import IAttributeChangeEvent, IAssociationChangeEvent
import operator


class umlproperty(object):
    """
    Superclass for attribute, enumeration and association.
    The subclasses should define a 'name' attribute that contains the name
    of the property. Derived properties (derivedunion and redefine) can be
    connected, they will be notified when the value changes.
    """

    def __get__(self, obj, class_=None):
        if obj:
            return self._get(obj)
        return self

    def __set__(self, obj, value):
        self._set(obj, value)

    def __delete__(self, obj, value=None):
        self._del(obj, value)

    def save(self, obj, save_func):
        if hasattr(obj, self._name):
            save_func(self.name, self._get(obj))

    def load(self, obj, value):
        self._set(obj, value)

    def postload(self, obj):
        pass

    def notify(self, obj):
        """
        Notify obj that the property's value has been changed.
        Deriviates are also triggered to send a notify signal.
        """
        try:
            obj.notify(self.name, pspec=self)
        except Exception, e:
            log.error(str(e), e)


class attribute(umlproperty):
    """
    Attribute.

    Element.attr = attribute('attr', types.StringType, '')
    """

    # TODO: check if lower and upper are actually needed for attributes
    def __init__(self, name, type, default=None, lower=0, upper=1):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.type = type
        self.default = default
        self.lower = lower
        self.upper = upper
        
    def load(self, obj, value):
        # FixMe: value might be a string while some other type is required:
        #print 'attribute.load:', self.name, self.type, value,
        if self.type is not object:
            value = self.type(value)
        setattr(obj, self._name, value)

    def __str__(self):
        if self.lower == self.upper:
            return '<attribute %s: %s[%s] = %s>' % (self.name, self.type, self.lower, self.default)
        else:
            return '<attribute %s: %s[%s..%s] = %s>' % (self.name, self.type, self.lower, self.upper, self.default)

    def _get(self, obj):
        try:
            return getattr(obj, self._name)
        except AttributeError:
            return self.default

    def _set(self, obj, value):
        if value is not None and not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % hasattr(self.type, '__name__') and self.type.__name__ or self.type

        if value == self._get(obj):
            return

        #undoattributeaction(self, obj, self._get(obj))

        old = self._get(obj)
        if value == self.default and hasattr(obj, self._name):
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        component.handle(AttributeChangeEvent(obj, self, old, value))
        self.notify(obj)

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            #undoattributeaction(self, obj, self._get(obj))
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            component.handle(AttributeChangeEvent(obj, self, old, self.default))
            self.notify(obj)


class enumeration(umlproperty):
    """
    Enumeration.
    Element.enum = enumeration('enum', ('one', 'two', 'three'), 'one')
    """

    def __init__(self, name, values, default):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.values = values
        self.default = default

    def __str__(self):
        return '<enumeration %s: %s = %s>' % (self.name, self.values, self.default)

    def _get(self, obj):
        try:
            return getattr(obj, self._name)
        except AttributeError:
            return self.default

    def load(self, obj, value):
        if not value in self.values:
            raise AttributeError, 'Value should be one of %s' % str(self.values)
        setattr(obj, self._name, value)

    def _set(self, obj, value):
        if not value in self.values:
            raise AttributeError, 'Value should be one of %s' % str(self.values)
        old = self._get(obj)
        if value == old:
            return

        #undoattributeaction(self, obj, self._get(obj))
        if value == self.default:
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        component.handle(AttributeChangeEvent(obj, self, old, value))
        self.notify(obj)

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            #undoattributeaction(self, obj, self._get(obj))
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            component.handle(AttributeChangeEvent(obj, self, old, self.default))
            self.notify(obj)


#class undosetassociationaction(undoaction):
#    """
#    Undo a 'set' action in an association.
#    """
#
#    def undo(self):
#        #log.debug('undosetassociationaction del: %s %s %s' % (self.obj, self.prop.name, self.value))
#        self.prop._del(self.obj, self.value)
#        return self.redo
#
#    def redo(self):
#        #log.debug('undosetassociationaction set: %s %s %s' % (self.obj, self.prop.name, self.value))
#        self.prop._set(self.obj, self.value)
##        return self.undo


#class undodelassociationaction(undoaction):
#    """Undo a 'del' action in an association.
#    """
#
#    def undo(self):
#        #log.debug('undodelassociationaction set: %s %s %s' % (self.obj, self.prop.name, self.value))
#        self.prop._set(self.obj, self.value)
#        return self.redo
#
#    def redo(self):
#        #log.debug('undodelassociationaction del: %s %s %s' % (self.obj, self.prop.name, self.value))
#        self.prop._del(self.obj, self.value)
#        return self.undo


class association(umlproperty):
    """
    Association, both uni- and bi-directional.

    Element.assoc = association('assoc', Element, opposite='other')
    
    A listerer is connected to the value added to the association. This
    will cause the association to be ended if the element on the other end
    of the association is unlinked.

    If the association is a composite relationship, the value is connected to
    the elements __unlink__ signal too. This will cause the value to be
    unlinked as soon as the element is unlinked.
    """
 
    def __init__(self, name, type, lower=0, upper='*', composite=False, opposite=None):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.type = type
        self.lower = lower
        self.upper = upper
        self.composite = composite
        self.opposite = opposite and intern(opposite)

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value for %s should be of type %s (%s)' % (self.name, self.type.__name__, type(value).__name__)
        self._set(obj, value, do_notify=False)

    def postload(self, obj):
        """In the postload step, ensure that bi-directional associations
        are bi-directional.
        """
        values = self._get(obj)
        if not values:
            return
        if self.upper == 1:
            values = [ values ]
        for value in values:
            if not isinstance(value, self.type):
                raise AttributeError, 'Error in postload validation for %s: Value %s should be of type %s' % (self.name, value, self.type.__name__)

    def __str__(self):
        if self.lower == self.upper:
            s = '<association %s: %s[%s]' % (self.name, self.type.__name__, self.lower)
        else:
            s = '<association %s: %s[%s..%s]' % (self.name, self.type.__name__, self.lower, self.upper)
        if self.opposite:
            s += ' %s-> %s' % (self.composite and '<>' or '', self.opposite)
        return s + '>'

    def _get(self, obj):
        #print '_get', self, obj
        # TODO: Handle lower and add items if lower > 0
        try:
            return getattr(obj, self._name)
        except AttributeError:
            if self.upper > 1:
                # Create the empty collection here since it might be used to
                # add 
                c = collection(self, obj, self.type)
                setattr(obj, self._name, c)
                return c
            else:
                return None

    def _set(self, obj, value, from_opposite=False, do_notify=True):
        """
        Set a new value for our attribute. If this is a collection, append
        to the existing collection.

        This method is called from the opposite association property.
        """
        #print '__set__', self, obj, value
        if not (isinstance(value, self.type) or \
                (value is None and self.upper == 1)):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        # Remove old value only for uni-directional associations
        if self.upper == 1:
            old = self._get(obj)

            # do nothing if we are assigned our current value:
            if value is old:
                return

            # is done in _del(): undoassociationaction(self, obj, old)
            if old:
                self._del(obj, old)

            if value is None:
                return

            #if value is self._get(obj):
            #    #log.debug('association: value already in obj: %s' % value)
            #    return

            #if not from_opposite:
            #    undosetassociationaction(self, obj, value)
            setattr(obj, self._name, value)
            if do_notify:
                event = AssociationSetEvent(obj, self, old, value)
        else:
            # Set the actual value
            c = self._get(obj)
            if not c:
                c = collection(self, obj, self.type)
                setattr(obj, self._name, c)
            elif value in c:
                #log.debug('association: value already in obj: %s' % value)
                return

            #if not from_opposite:
            #    undosetassociationaction(self, obj, value)
            c.items.append(value)
            if do_notify:
                event = AssociationAddEvent(obj, self, value)

        # Callbacks are only connected if a new relationship has
        # been established.
        value.connect('__unlink__', self.__on_unlink, obj)
        if self.composite:
            obj.connect('__unlink__', self.__on_composite_unlink, value)
        
        if not from_opposite and self.opposite:
            getattr(type(value), self.opposite)._set(value, obj, from_opposite=True, do_notify=do_notify)

        if do_notify:
            self.notify(obj)
            component.handle(event)

    def _del(self, obj, value, from_opposite=False):
        """
        Delete is used for element deletion and for removal of
        elements from a list.
        """
        #print '__delete__', self, obj, value

        if not value:
            if self.upper > 1:
                raise Exception, 'Can not delete collections'
            old = value = self._get(obj)
            if value is None:
                return

        #if not from_opposite:
        #    undodelassociationaction(self, obj, value)

        if not from_opposite and self.opposite:
            getattr(type(value), self.opposite)._del(value, obj, from_opposite=True)

        if self.upper > 1:
            c = self._get(obj)
            if c:
                items = c.items
                try:
                    items.remove(value)
                except:
                    pass
                else:
                    component.handle(AssociationDeleteEvent(obj, self, value))
                # Remove items collection if empty
                if not items:
                    delattr(obj, self._name)
        else:
            try:
                delattr(obj, self._name)
            except:
                pass
                #print 'association._del: delattr failed for %s' % self.name
            else:
                component.handle(AssociationSetEvent(obj, self, value, None))

        value.disconnect(self.__on_unlink, obj)
        if self.composite:
            obj.disconnect(self.__on_composite_unlink, value)
        self.notify(obj)

    def __on_unlink(self, value, pspec, obj):
        """
        Disconnect when the element on the other end of the association
        (value) sends the '__unlink__' signal. This is especially important
        for uni-directional associations.
        """
        #print '__on_unlink', name, obj, value
        if pspec == '__unlink__':
            self.__delete__(obj, value)
            # re-establish unlink handler:
            value.connect('__unlink__', self.__on_unlink, obj)

    def __on_composite_unlink(self, obj, pspec, value):
        """
        Unlink value if we have a part-whole (composite) relationship
        (value is a composite of obj).
        The implementation of value.unlink() should ensure that no deadlocks
        occur.
        """
        #print '__on_composite_unlink:', self, name, value
        if pspec == '__unlink__':
            value.unlink()
            obj.connect('__unlink__', self.__on_composite_unlink, value)
        #else:
            #print 'RELINK'
            #value.relink()


class derivedunion(umlproperty):
    """
    Derived union
    Element.union = derivedunion('union', subset1, subset2..subsetn)
    The subsets are the properties that participate in the union (Element.name),
    """

    def __init__(self, name, lower, upper, *subsets):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.lower = lower
        self.upper = upper
        self.subsets = set(subsets)
        self.single = len(subsets) == 1

        component.provideHandler(self._association_changed)


    def load(self, obj, value):
        raise ValueError, 'Derivedunion: Properties should not be loaded in a derived union %s: %s' % (self.name, value)


    def save(self, obj, save_func):
        pass


    def __str__(self):
        return '<derivedunion %s: %s>' % (self.name, str(map(str, self.subsets))[1:-1])


    def _get(self, obj):
        if self.single:
            #return getattr(obj, self.subsets[0])
            return self.subsets[0].__get__(obj)
        else:
            u = list()
            for s in self.subsets:
                tmp = s.__get__(obj)
                if tmp:
                    # append or extend tmp (is it a list or not)
                    try:
                        for t in tmp:
                            if t not in u:
                                u.append(t)
                        #u.extend(tmp)
                    except TypeError:
                        if tmp not in u:
                            u.append(tmp)
            if self.upper > 1:
                return u
            else:
                assert len(u) <= 1, 'Derived union %s of item %s should have length 1 %s' % (self.name, obj.id, tuple(u))
                return u and u[0] or None


    def _set(self, obj, value):
        raise AttributeError, 'Can not set values on a union'


    def _del(self, obj, value=None):
        raise AttributeError, 'Can not delete values on a union'


    @component.adapter(IAssociationChangeEvent)
    def _association_changed(self, event):
        if event.property in self.subsets:
            # mimic the events for Set/Add/Delete
            if isinstance(event, AssociationSetEvent):
                component.handle(AssociationSetEvent(event.element, self, event.old_value, event.new_value))
            elif isinstance(event, AssociationAddEvent):
                component.handle(AssociationAddEvent(event.element, self, event.new_value))
            elif isinstance(event, AssociationDeleteEvent):
                component.handle(AssociationDeleteEvent(event.element, self, event.old_value))
            else:
                log.error('Don''t know how to handle event ' + str(event) + ' for derived union')
            self.notify(event.element)


class redefine(umlproperty):
    """
    Redefined association
    Element.x = redefine('x', Class, Element.assoc)
    If the redefine eclipses the original property (it has the same name)
    it ensures that the original values are saved and restored.
    """

    def __init__(self, name, type, original):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.type = type
        self.original = original

        component.provideHandler(self._association_changed)

    upper = property(lambda s: s.original.upper)
    lower = property(lambda s: s.original.lower)


    def load(self, obj, value):
        if self.original.name == self.name:
            self.original.load(obj, value)


    def save(self, obj, save_func):
        if self.original.name == self.name:
            self.original.save(obj, save_func)


    def __str__(self):
        return '<redefine %s: %s = %s>' % (self.name, self.type.__name__, str(self.original))


    def __get__(self, obj, class_=None):
        # No longer needed
        if not obj:
            return self
        return self.original.__get__(obj, class_)


    def __set__(self, obj, value):
        # No longer needed
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self.original.__set__(obj, value)


    def __delete__(self, obj, value=None):
        # No longer needed
        self.original.__delete__(obj, value)


    def _get(self, obj):
        return self.original._get(obj)


    def _set(self, obj, value, from_opposite=False):
        return self.original._set(obj, value, from_opposite)


    def _del(self, obj, value, from_opposite=False):
        return self.original._del(obj, value, from_opposite)


    @component.adapter(IAssociationChangeEvent)
    def _association_changed(self, event):
        if event.property is self.original:
            # mimic the events for Set/Add/Delete
            if isinstance(event, AssociationSetEvent):
                component.handle(AssociationSetEvent(event.element, self, event.old_value, event.new_value))
            elif isinstance(event, AssociationAddEvent):
                component.handle(AssociationAddEvent(event.element, self, event.new_value))
            elif isinstance(event, AssociationDeleteEvent):
                component.handle(AssociationDeleteEvent(event.element, self, event.old_value))
            else:
                log.error('Don''t know how to handle event ' + str(event) + ' for redefined association')
            self.notify(event.element)


try:
    import psyco
except ImportError:
    pass
else:
    psyco.bind(umlproperty)
    psyco.bind(attribute)
    psyco.bind(enumeration)
    psyco.bind(association)
    psyco.bind(derivedunion)
    psyco.bind(redefine)
