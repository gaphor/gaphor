#!/usr/bin/env python
# vim:sw=4:et
"""Properties used to create the UML 2.0 data model.

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
    (_set2(value):    used by association, used to set bi-directional ass.)
    _del(value=None): delete the value. 'value' is used to tell which value
                      is to be removed (in case of associations with
                      multiplicity > 1).
    load(value):      load 'value' as the current value for this property
    save(save_func):  send the value of the property to save_func(name, value)
    #unlink():         remove references to other elements.
"""

__all__ = [ 'attribute', 'enumeration', 'association', 'derivedunion', 'redefine' ]

from collection import collection
import operator
from gaphor.undomanager import get_undo_manager

#infinite = 100000

class attributeundoaction(object):
    """This undo action contains one undo action for an attribute
    property.
    """

    def __init__(self, prop, obj, value):
        self.prop = prop
        self.obj = obj
        self.value = value
        get_undo_manager().add_undo_action(self)

    def undo(self):
        self.redo_value = self.prop._get(self.obj)
        setattr(self.obj, self.prop._name, self.value)
        self.prop.notify(self.obj)

    def redo(self):
        setattr(self.obj, self.prop._name, self.redo_value)
        self.prop.notify(self.obj)

class associationundoaction(object):
    """The state of an association can be reverted with this action.
    """

    def __init__(self, prop, obj, value):
        self.prop = prop
        self.obj = obj
        self.value = value
        #print 'adding undo action', prop, obj, value
        get_undo_manager().add_undo_action(self)

    def undo(self):
        """Undo an event. This is very hard to read.
        TODO: cleanup and structure association code!!!!!
        TODO: self.value returns to [] on undo
        """
        prop = self.prop
        obj = self.obj
        log.debug('undo association %s' % prop.name)
        if prop.upper > 1:
            l = prop._get(obj)
            self.redo_value = list(l)
            #print 'redo_value =', self.redo_value, self.value
            for item in l:
                if item not in self.value:
                    if prop.opposite:
                        getattr(type(item), prop.opposite)._del(item, obj)
                    prop._del(obj, item)
            l = prop._get(obj)
            for item in self.value:
                if item not in l:
                    if prop._set2(obj, item):
                        # Set opposite side.
                        # Use type(value) since the property may be overridden:
                        if prop.opposite:
                            getattr(type(item), prop.opposite)._set(item, obj)
            #print 'redo_value =', self.redo_value, self.value
            prop.notify(obj)
        else:
            value = self.redo_value = prop._get(obj)
            if self.value is None:
                # _del does a notify().
                if value is None:
                    return
                if prop.opposite:
                    getattr(type(value), prop.opposite)._del(value, obj)
                prop._del(obj, prop._get(obj))
            else:
                if prop._set2(obj, self.value):
                    if prop.opposite:
                        getattr(type(value), prop.opposite)._set(value, obj)
                prop.notify(obj)

    def redo(self):
        prop = self.prop
        obj = self.obj
        log.debug('redo association %s' % prop.name)
        if prop.upper > 1:
            #print 'setting... on', prop, obj, self.redo_value
            l = prop._get(obj)
            for item in l:
                if item not in self.redo_value:
                    if prop.opposite:
                        getattr(type(item), prop.opposite)._del(item, obj)
                    prop._del(obj, item)
            l = prop._get(obj)
            for item in self.redo_value:
                if item not in l:
                    if prop._set2(obj, item):
                        # Set opposite side.
                        # Use type(value) since the property may be overridden:
                        if prop.opposite:
                            getattr(type(item), prop.opposite)._set(item, obj)
            #print prop._get(obj), self.redo_value
            prop.notify(obj)
        else:
            #self.redo_value = prop._get(obj)
            #print self.redo_value
            if self.redo_value is None:
                # _del does a notify().
                value = prop._get(obj) 
                if value is None:
                    return
                if prop.opposite:
                    getattr(type(value), prop.opposite)._del(value, obj)
                prop._del(obj, prop._get(obj))
            else:
                if prop._set2(obj, self.redo_value):
                    if prop.opposite:
                        getattr(type(self.redo_value), prop.opposite)._set(self.redo_value, obj)
                prop.notify(obj)


class umlproperty(object):
    """Superclass for attribute, enumeration and association.
    The subclasses should define a 'name' attribute that contains the name
    of the property. Derived properties (derivedunion and redefine) can be
    connected, they will be notified when the value changes.
    """

    def add_deriviate(self, deriviate):
        try:
            self.deriviates.append(deriviate)
        except AttributeError:
            self.deriviates = [ deriviate ]

    def __get__(self, obj, class_=None):
        if not obj:
            return self
        return self._get(obj)

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

#    def unlink(self, obj):
#        if hasattr(obj, self._name):
#            self.__delete__(obj)

    def notify(self, obj):
        """Notify obj that the property's value has been changed.
        Deriviates are also triggered to send a notify signal.
        """
        try:
            obj.notify(self.name, pspec=self)
        except Exception, e:
            log.error(str(e), e)

        # we need to check if a deriviate is part of the current object:
        # TODO: can we do this faster?
        try:
            deriviates = self.deriviates
        except AttributeError:
            pass # no derivedunion or redefine attribute
        else:
            values = []
            for c in type(obj).__mro__:
                values.extend(c.__dict__.values())

            for d in deriviates:
                if d in values:
                    try:
                        d.notify(obj)
                    except Exception, e:
                        log.error(e, e)


class attribute(umlproperty):
    """Attribute.
    Element.attr = attribute('attr', types.StringType, '')"""

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

        attributeundoaction(self, obj, self._get(obj))

        if value == self.default and hasattr(obj, self._name):
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.notify(obj)

    def _del(self, obj, value=None):
        #self.old = self._get(obj)
        try:
            attributeundoaction(self, obj, self._get(obj))
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.notify(obj)


class enumeration(umlproperty):
    """Enumeration.
    Element.enum = enumeration('enum', ('one', 'two', 'three'), 'one')"""

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
        if value != self._get(obj):
            attributeundoaction(self, obj, self._get(obj))
            if value == self.default:
                delattr(obj, self._name)
            else:
                setattr(obj, self._name, value)
            self.notify(obj)

    def _del(self, obj, value=None):
        try:
            attributeundoaction(self, obj, self._get(obj))
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.notify(obj)


class association(umlproperty):
    """Association, both uni- and bi-directional.
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
        if self._set2(obj, value) and self.opposite:
            opposite = getattr(type(value), self.opposite)
            if opposite.upper > 1:
                if not obj in opposite._get(value):
                    #print 'Setting opposite*:', self.name, str(opposite), obj, value
                    opposite._set2(value, obj)
            else:
                if not obj is opposite._get(value):
                    #print 'Setting opposite1:', self.name, obj, value
                    opposite._set2(value, obj)

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

    def __get__(self, obj, class_=None):
        """Retrieve the value of the association. In case this is called
        directly on the class, return self."""
        #print '__get__', self, obj, class_
        if not obj:
            return self
        return self._get(obj)

    def __set__(self, obj, value):
        """Set a new value for our attribute. If this is a collection, append
        to the existing collection."""
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
            associationundoaction(self, obj, old)
            if old:
                self.__delete__(obj, old)
            if value is None:
                #self.notify(obj)
                return
        else:
            associationundoaction(self, obj, list(self._get(obj)))

        # if we needed to set our own side, set the opposite
        # Call _set2() so we can make sure the opposite side is set before
        # a signal is emited.
        if self._set2(obj, value):
            # Set opposite side.
            # Use type(value) since the property may be overridden:
            if self.opposite:
                getattr(type(value), self.opposite)._set(value, obj)
            self.notify(obj)

    def __delete__(self, obj, value=None):
        """Delete is used for element deletion and for removal of
        elements from a list.
        """
        #print '__delete__', self, obj, value
        if self.upper > 1 and not value:
            raise Exception, 'Can not delete collections'
        if not value:
            value = self._get(obj)
            if value is None:
                return
        # Save undo info
        if self.upper > 1:
            associationundoaction(self, obj, list(self._get(obj)))
        else:
            associationundoaction(self, obj, self._get(obj))

        if self.opposite:
            getattr(type(value), self.opposite)._del(value, obj)
        self._del(obj, value)
        
    def _get(self, obj):
        #print '_get', self, obj
        # TODO: Handle lower and add items if lower > 0
        try:
            return getattr(obj, self._name)
        except AttributeError:
            if self.upper > 1:
                # Create the empty collection here since it might be used to
                # add 
                #c = collection(self, obj, self.type)
                #setattr(obj, self._name, c)
                return []
            else:
                return None

    def _set(self, obj, value):
        #print '_set', self, obj, value
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        if self._set2(obj, value):
            self.notify(obj)

    def _set2(self, obj, value):
        """Real setter, avoid doing the assertion check twice.
        Return True if notification should be send, False otherwise."""
        if self.upper > 1:
            c = self._get(obj)
            if not c:
                c = collection(self, obj, self.type)
                setattr(obj, self._name, c)
            elif value in c:
                #log.debug('association: value already in obj: %s' % value)
                return False
            c.items.append(value)
        else:
            if value is self._get(obj):
                #log.debug('association: value already in obj: %s' % value)
                return False
            setattr(obj, self._name, value)

        # Callbacks are only connected if a new relationship has
        # been established.
        value.connect('__unlink__', self.__on_unlink, obj)
        if self.composite:
            obj.connect('__unlink__', self.__on_composite_unlink, value)
        return True

    def _del(self, obj, value):
        """Delete value from the association."""
        #print '_del', self, obj, value
        if self.upper > 1:
            c = self._get(obj)
            if c:
                items = c.items
                try:
                    items.remove(value)
                except:
                    pass
                if not items:
                    delattr(obj, self._name)
        else:
            try:
                delattr(obj, self._name)
            except:
                pass
                #print 'association._del: delattr failed for %s' % self.name
        value.disconnect(self.__on_unlink, obj)
        if self.composite:
            obj.disconnect(self.__on_composite_unlink, value)
        self.notify(obj)

#    def unlink(self, obj):
#        #print 'unlink', self, obj
#        lst = getattr(obj, self._name)
#        while lst:
#            self.__delete__(obj, lst[0])
#            # re-establish unlink handler:
#            value.connect('__unlink__', self.__on_unlink, obj)

    def __on_unlink(self, value, pspec, obj):
        """Disconnect when the element on the other end of the association
        (value) sends the '__unlink__' signal. This is especially important
        for uni-directional associations.
        """
        #print '__on_unlink', name, obj, value
        if pspec == '__unlink__':
            self.__delete__(obj, value)
            # re-establish unlink handler:
            value.connect('__unlink__', self.__on_unlink, obj)
        #else:
        #    print 'RELINK'
        #    self.__set__(obj, value)

    def __on_composite_unlink(self, obj, pspec, value):
        """Unlink value if we have a part-whole (composite) relationship
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
    """Derived union
    Element.union = derivedunion('union', subset1, subset2..subsetn)
    The subsets are the properties that participate in the union (Element.name),

    The derivedunion is added to the subsets deriviates list.
    """

    def __init__(self, name, lower, upper, *subsets):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.lower = lower
        self.upper = upper
        self.subsets = subsets
        self.single = len(subsets) == 1
        for s in subsets:
            s.add_deriviate(self)

    def load(self, obj, value):
        raise ValueError, 'Derivedunion: Properties should not be loaded in a derived union %s: %s' % (self.name, value)

    def save(self, obj, save_func):
        pass

#    def unlink(self, obj):
#        pass

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


class redefine(umlproperty):
    """Redefined association
    Element.x = redefine('x', Class, Element.assoc)
    If the redefine eclipses the original property (it has the same name)
    it ensures that the original values are saved and restored.

    This property is connected to the originals deriviates list.
    """

    def __init__(self, name, type, original):
        self.name = intern(name)
        self._name = intern('_' + name)
        self.type = type
        self.original = original
        original.add_deriviate(self)

    upper = property(lambda s: s.original.upper)
    lower = property(lambda s: s.original.lower)

    def load(self, obj, value):
        if self.original.name == self.name:
            self.original.load(obj, value)

    def save(self, obj, save_func):
        if self.original.name == self.name:
            self.original.save(obj, save_func)

#    def unlink(self, obj):
#        self.original.unlink(obj)

    def __str__(self):
        return '<redefine %s: %s = %s>' % (self.name, self.type.__name__, str(self.original))

    def _get(self, obj):
        return self.original._get(obj)

    def _set(self, obj, value):
        return self.original._set(obj, value)

    def _set2(self, obj, value):
        return self.original._set2(obj, value)

    def __get__(self, obj, class_=None):
        if not obj:
            return self
        return self.original.__get__(obj, class_)

    def __set__(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self.original.__set__(obj, value)

    def __delete__(self, obj, value=None):
        self.original.__delete__(obj, value)

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
