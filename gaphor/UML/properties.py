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
    unlink():         remove references to other elements.
"""

__all__ = [ 'attribute', 'enumeration', 'association', 'derivedunion', 'redefine' ]

from collection import collection
import operator

#infinite = 100000

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

    def __get__(self, obj, clazz=None):
        if not obj:
            return self
        return self._get(obj)

    def __set__(self, obj, value):
        self._set(obj, value)

    def __delete__(self, obj, value=None):
        self._del(obj, value)

    def load(self, obj, value):
        self._set(obj, value)

    def save(self, obj, save_func):
        if hasattr(obj, '_' + self.name):
            save_func(self.name, self._get(obj))

    def unlink(self, obj):
        if hasattr(obj, '_' + self.name):
            self.__delete__(obj)

    def notify(self, obj):
        """Notify obj that the property's value has been changed.
        Deriviates are also triggered to send a notify signal."""
        try:
            obj.notify(self.name)
        except:
            pass

        # we need to check if a deriviate is part of the current object:
        # TODO: can we do this faster?
        mro = obj.__class__.__mro__
        try:
            for d in self.deriviates:
                for c in mro:
                    if d in c.__dict__.values():
                        d.notify(obj)
        except AttributeError:
            pass # no derivedunion or redefine attribute


class attribute(umlproperty):
    """Attribute.
    Element.attr = attribute('attr', types.StringType, '')"""

    # TODO: check if lower and upper are actually needed for attributes
    def __init__(self, name, type, default, lower=0, upper=1):
        self.name = name
        self.type = type
        self.default = default
        self.lower = lower
        self.upper = upper
        
    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s (is %s)' % (self.type.__name__, type(value))
        setattr(obj, '_' + self.name, value)

    def __str__(self):
        if self.lower == self.upper:
            return '<attribute %s: %s[%s] = %s>' % (self.name, self.type, self.lower, self.default)
        else:
            return '<attribute %s: %s[%s..%s] = %s>' % (self.name, self.type, self.lower, self.upper, self.default)

    def _get(self, obj):
        try:
            return getattr(obj, '_' + self.name)
        except AttributeError:
            return self.default

    def _set(self, obj, value):
        if value is not None and not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % hasattr(self.type, '__name__') and self.type.__name__ or self.type
        if value == self.default and hasattr(obj, '_' + self.name):
            delattr(obj, '_' + self.name)
        else:
            setattr(obj, '_' + self.name, value)
        self.notify(obj)

    def _del(self, obj, value=None):
        delattr(obj, '_' + self.name)
        self.notify(obj)


class enumeration(umlproperty):
    """Enumeration.
    Element.enum = enumeration('enum', ('one', 'two', 'three'), 'one')"""

    def __init__(self, name, values, default):
        self.name = name
        self.values = values
        self.default = default

    def __str__(self):
        return '<enumeration %s: %s = %s>' % (self.name, self.values, self.default)

    def _get(self, obj):
        try:
            return getattr(obj, '_' + self.name)
        except AttributeError:
            return self.default

    def load(self, obj, value):
        if not value in self.values:
            raise AttributeError, 'Value should be in %s' % str(self.values)
        setattr(obj, '_' + self.name, value)

    def _set(self, obj, value):
        if not value in self.values:
            raise AttributeError, 'Value should be in %s' % str(self.values)
        if value != self._get(obj):
            if value == self.default:
                delattr(obj, '_' + self.name)
            else:
                setattr(obj, '_' + self.name, value)
            self.notify(obj)

    def _del(self, obj, value=None):
        delattr(obj, '_' + self.name)
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
        self.name = name
        self.type = type
        self.lower = lower
        self.upper = upper
        self.composite = composite
        self.opposite = opposite

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self._set2(obj, value)

    def __str__(self):
        if self.lower == self.upper:
            s = '<association %s: %s[%s]' % (self.name, self.type.__name__, self.lower)
        else:
            s = '<association %s: %s[%s..%s]' % (self.name, self.type.__name__, self.lower, self.upper)
        if self.opposite:
            s += ' -> %s' % self.opposite
        return s + '>'

    def __get__(self, obj, clazz=None):
        """Retrieve the value of the association. In case this is called
        directly on the class, return self."""
        #print '__get__', self, obj, clazz
        if not obj:
            return self
        return self._get(obj)

    def __set__(self, obj, value):
        """Set a new value for our attribute. If this is a collection, append
        to the existing collection."""
        #print '__set__', self, obj, value
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        # Remove old value only for uni-directional associations
        if self.upper == 1:
            old = self._get(obj)
            if old:
                self.__delete__(obj, old)
        self._set2(obj, value)
        # Set opposite side:
        if self.opposite:
            getattr(self.type, self.opposite)._set(value, obj)
        self.notify(obj)

    def __delete__(self, obj, value=None):
        """Delete is used for element deletion and for removal of elements from
        a list."""
        #print '__delete__', self, obj, value
        if self.upper > 1 and not value:
            raise Exception, 'Can not delete collections'
        if self.opposite:
            getattr(self.type, self.opposite)._del(value or self._get(obj), obj)
        self._del(obj, value or self._get(obj))
        
    def _get(self, obj):
        #print '_get', self, obj
        # TODO: Handle lower and add items if lower > 0
        try:
            return getattr(obj, '_' + self.name)
        except AttributeError:
            if self.upper > 1:
                l = collection(self, obj, self.type)
                setattr(obj, '_' + self.name, l)
                return l
            else:
                return None

    def _set(self, obj, value):
        #print '_set', self, obj, value
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self._set2(obj, value)
        self.notify(obj)

    def _set2(self, obj, value):
        """Real setter, avoid doing the assertion check twice."""
        if self.upper > 1:
            if value in self._get(obj):
                return
            self._get(obj).items.append(value)
        else:
            setattr(obj, '_' + self.name, value)
        value.connect('__unlink__', self.__on_unlink, obj, value)
        if self.composite:
            obj.connect('__unlink__', self.__on_composite_unlink, value)

    def _del(self, obj, value):
        """Delete value from the association."""
        #print '_del', self, obj, value
        if self.upper > 1:
            items = self._get(obj).items
            items.remove(value)
            if not items:
                delattr(obj, '_' + self.name)
        else:
            delattr(obj, '_' + self.name)
        value.disconnect(self.__on_unlink, obj, value)
        if self.composite:
            obj.disconnect(self.__on_composite_unlink, value)
        self.notify(obj)

    def unlink(self, obj):
        lst = getattr(obj, '_' + self.name)
        while lst:
            self.__delete__(obj, lst[0])

    def __on_unlink(self, name, obj, value):
        """Disconnect when the element on the other end of the association
        (value) sends the '__unlink__' signal. This is especially important
        for uni-directional associations.
        """
        #print '__on_unlink:', self, name, obj, value
        self.__delete__(obj, value)

    def __on_composite_unlink(self, name, value):
        """Unlink value if we have a part-whole (composite) relationship
        (value is a composite of obj).
        The implementation of value.unlink() should ensure that no deadlocks
        occur.
        """
        #print '__on_composite_unlink:', self, name, value
        value.unlink()


class derivedunion(umlproperty):
    """Derived union
    Element.union = derivedunion('union', subset1, subset2..subsetn)
    The subsets are the properties that participate in the union (Element.name),

    The derivedunion is added to the subsets deriviates list.
    """

    def __init__(self, name, lower, upper, *subsets):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.subsets = subsets
        self.single = len(subsets) == 1
        for s in subsets:
            s.add_deriviate(self)

    def load(self, obj, value):
        pass

    def save(self, obj, save_func):
        pass

    def unlink(self, obj):
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
                #tmp = getattr(obj, s)
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
                assert len(u) <= 1, 'Derived union %s should have length 1 %s' % (self.name, tuple(u))
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
        self.name = name
        self.type = type
        self.original = original
        original.add_deriviate(self)

    def load(self, obj, value):
        if self.original.name == self.name:
            self.original.load(obj, value)

    def save(self, obj, save_func):
        if self.original.name == self.name:
            self.original.save(obj, save_func)

    def unlink(self, obj):
        self.original.unlink(obj)

    def __str__(self):
        return '<redefine %s: %s = %s>' % (self.name, self.type.__name__, str(self.original))

    def __get__(self, obj, clazz=None):
        if not obj:
            return self
        return self.original.__get__(obj, clazz)

    def __set__(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self.original.__set__(obj, value)

    def __delete__(self, obj, value=None):
        self.original.__delete__(obj, value)

