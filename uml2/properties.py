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
    _del(value=None): delete the value. 'value' is used to tell which value
                      is to be removed (in case of associations with
                      multiplicity > 1).
    load(value):      load 'value' as the current value for this property
    save(save_func):  send the value of the property to save_func(name, value)
    unlink():         remove references to other elements.
"""

from collection import Collection

infinite = 100000

class umlproperty(object):
    """Superclass for attribute, enumeration and association."""
    name='umlproperty'

    def __get__(self, obj, clazz=None):
        if not obj:
            return self
        return self._get(obj)

    def __set__(self, obj, value):
        self._set(obj, value)

    def __delete__(self, obj, value=None):
        self._del(obj)

    def load(self, obj, value):
        self._set(obj, value)

    def save(self, obj, save_func):
        if hasattr(obj, '_' + self.name):
            save_func(self.name, self._get(obj))

    def unlink(self, obj):
        if hasattr(obj, '_' + self.name):
            self.__delete__(obj)

    def notify(self, obj):
        """Notify obj that the property's value has been changed"""
        try:
            obj.notify(self.name)
        except:
            pass


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
        
    def _get(self, obj):
        try:
            return getattr(obj, '_' + self.name)
        except AttributeError:
            return self.default

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        setattr(obj, '_' + self.name, value)

    def _set(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        if value == self.default:
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
    Element.assoc = association('assoc', Element, opposite='other')"""

    def __init__(self, name, type, lower=0, upper='*', opposite=None):
        self.name = name
        self.type = type
        self.lower = lower
        self.upper = upper
        self.opposite = opposite

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        if self.upper > 1:
            self._get(obj).items.append(value)
        else:
            setattr(obj, '_' + self.name, value)

    def __str__(self):
        if self.lower == self.upper:
            return '<association %s: %s[%s]>' % (self.name, self.type.__name__, self.lower)
        else:
            return '<association %s: %s[%s..%s]>' % (self.name, self.type.__name__, self.lower, self.upper)

    __repr__ = __str__

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
        # Set opposite side:
        if self.opposite:
            getattr(self.type, self.opposite)._set(value, obj)
        self.__set(obj, value)

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
                l = Collection(self, obj, self.type)
                setattr(obj, '_' + self.name, l)
                return l
            else:
                return None

    def _set(self, obj, value):
        #print '_set', self, obj, value
        if not isinstance(value, self.type):
            raise AttributeError, 'Value should be of type %s' % self.type.__name__
        self.__set(obj, value)

    def __set(self, obj, value):
        """Real setter, avoid doing the assertion check twice."""
        if self.upper > 1:
            if value in self._get(obj):
                return
            self._get(obj).items.append(value)
        else:
            setattr(obj, '_' + self.name, value)
        value.attach(('__unlink__',), self.__on_unlink, obj, value)
        self.notify(obj)

    def _del(self, obj, value):
        #print '_del', self, obj, value
        if self.upper > 1:
            items = self._get(obj).items
            items.remove(value)
            if not items:
                delattr(obj, '_' + self.name)
        else:
            delattr(obj, '_' + self.name)
        value.detach(self.__on_unlink, obj, value)
        self.notify(obj)

    def unlink(self, obj):
        lst = getattr(obj, '_' + self.name)
        while lst:
            self.__delete__(obj, lst[0])

    def notify(self, obj):
        """Notify that the property has changed. Also let derived unions
        notify.
        TODO: does this also apply to attributes and enumerations?
        """
        umlproperty.notify(self, obj)

        # Also notify derived unions that superset this property
        # This is done by finding derived unions in the class' dict that
        # contain references to this association.
        # Optimized for speed:
        _ii = isinstance
        _du = derivedunion
        for u in obj.__class__.__dict__.values():
            if _ii(u, _du) and self in u:
                u.notify(obj)

    def __on_unlink(self, name, obj, value):
        """Disconnect when the element on the other end of the association
        sends the '__unlink__' signal. This is especially important for
        uni-directional associations.
        """
        #print '__on_unlink:', self, name, obj, value
        self.__delete__(obj, value)


class derivedunion(umlproperty):
    """Derived union
    Element.union = derivedunion('union', subset1, subset2..subsetn)
    The subsets are the properties that participate in the union (Element.name),
    """

    def __init__(self, name, *subsets):
        self.name = name
        self.subsets = subsets
        self.single = len(subsets) == 1

    def load(self, obj, value):
        pass

    def save(self, obj, save_func):
        pass

    def unlink(self, obj):
        pass

    def __contains__(self, obj):
        """Returns if 'obj' is in the subsets list."""
        return obj in self.subsets

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
                        u.extend(tmp)
                    except TypeError:
                        u.append(tmp)
            return u

    def _set(self, obj, value):
        raise AttributeError, 'Can not set values on a union'

    def _del(self, obj, value=None):
        raise AttributeError, 'Can not delete values on a union'

