##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interface object implementation

$Id$
"""

from __future__ import generators

import sys
import warnings
import weakref
from types import FunctionType
from ro import ro
from zope.interface.exceptions import Invalid

CO_VARARGS = 4
CO_VARKEYWORDS = 8
TAGGED_DATA = '__interface_tagged_values__'

_decorator_non_return = object()

def invariant(call):
    f_locals = sys._getframe(1).f_locals
    tags = f_locals.get(TAGGED_DATA)
    if tags is None:
        tags = f_locals[TAGGED_DATA] = {}
    invariants = tags.get('invariants')
    if invariants is None:
        invariants = tags['invariants'] = []
    invariants.append(call)
    return _decorator_non_return

class Element(object):

    # We can't say this yet because we don't have enough
    # infrastructure in place.
    #
    #implements(IElement)

    def __init__(self, __name__, __doc__=''):
        """Create an 'attribute' description
        """
        if not __doc__ and __name__.find(' ') >= 0:
            __doc__ = __name__
            __name__ = None

        self.__name__=__name__
        self.__doc__=__doc__
        self.__tagged_values = {}

    def getName(self):
        """ Returns the name of the object. """
        return self.__name__

    def getDoc(self):
        """ Returns the documentation for the object. """
        return self.__doc__

    def getTaggedValue(self, tag):
        """ Returns the value associated with 'tag'. """
        return self.__tagged_values[tag]

    def queryTaggedValue(self, tag, default=None):
        """ Returns the value associated with 'tag'. """
        return self.__tagged_values.get(tag, default)

    def getTaggedValueTags(self):
        """ Returns a list of all tags. """
        return self.__tagged_values.keys()

    def setTaggedValue(self, tag, value):
        """ Associates 'value' with 'key'. """
        self.__tagged_values[tag] = value

class SpecificationBasePy(object):

    def providedBy(self, ob):
        """Is the interface implemented by an object

          >>> from zope.interface import *
          >>> class I1(Interface):
          ...     pass
          >>> class C(object):
          ...     implements(I1)
          >>> c = C()
          >>> class X(object):
          ...     pass
          >>> x = X()
          >>> I1.providedBy(x)
          False
          >>> I1.providedBy(C)
          False
          >>> I1.providedBy(c)
          True
          >>> directlyProvides(x, I1)
          >>> I1.providedBy(x)
          True
          >>> directlyProvides(C, I1)
          >>> I1.providedBy(C)
          True
        
        """
        spec = providedBy(ob)
        return self in spec._implied

    def implementedBy(self, cls):
        """Do instances of the given class implement the interface?"""
        spec = implementedBy(cls)
        return self in spec._implied

    def isOrExtends(self, interface):
        """Is the interface the same as or extend the given interface

        Examples::

          >>> from zope.interface import Interface
          >>> from zope.interface.declarations import Declaration
          >>> class I1(Interface): pass
          ...
          >>> class I2(I1): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(I3): pass
          ...
          >>> spec = Declaration()
          >>> int(spec.extends(Interface))
          0
          >>> spec = Declaration(I2)
          >>> int(spec.extends(Interface))
          1
          >>> int(spec.extends(I1))
          1
          >>> int(spec.extends(I2))
          1
          >>> int(spec.extends(I3))
          0
          >>> int(spec.extends(I4))
          0

        """
        return interface in self._implied

SpecificationBase = SpecificationBasePy

try:
    from _zope_interface_coptimizations import SpecificationBase
except ImportError:
    pass

class Specification(SpecificationBase):
    """Specifications

    An interface specification is used to track interface declarations
    and component registrations.

    This class is a base class for both interfaces themselves and for
    interface specifications (declarations).

    Specifications are mutable.  If you reassign their cases, their
    relations with other specifications are adjusted accordingly.

    For example:

    >>> from zope.interface import Interface
    >>> class I1(Interface):
    ...     pass
    >>> class I2(I1):
    ...     pass
    >>> class I3(I2):
    ...     pass

    >>> [i.__name__ for i in I1.__bases__]
    ['Interface']

    >>> [i.__name__ for i in I2.__bases__]
    ['I1']

    >>> I3.extends(I1)
    1

    >>> I2.__bases__ = (Interface, )

    >>> [i.__name__ for i in I2.__bases__]
    ['Interface']

    >>> I3.extends(I1)
    0
        
    """

    # Copy some base class methods for speed
    isOrExtends = SpecificationBase.isOrExtends
    providedBy = SpecificationBase.providedBy

    #########################################################################
    # BBB 2004-07-13: Backward compatabilty.  These methods have been
    # deprecated in favour of providedBy and implementedBy.

    def isImplementedByInstancesOf(self, cls):
        warnings.warn(
            "isImplementedByInstancesOf has been renamed to implementedBy",
            DeprecationWarning, stacklevel=2,
            )
        return self.implementedBy(cls)

    def isImplementedBy(self, ob):
        warnings.warn(
            "isImplementedBy has been renamed to providedBy",
            DeprecationWarning, stacklevel=2,
            )
        return self.providedBy(ob)
    #
    #########################################################################

    def __init__(self, bases=()):
        self._implied = {}
        self.dependents = weakref.WeakKeyDictionary()
        self.__bases__ = tuple(bases)

    def subscribe(self, dependent):
        self.dependents[dependent] = 1

    def unsubscribe(self, dependent):
        del self.dependents[dependent]

    def __setBases(self, bases):
        # Register ourselves as a dependent of our old bases
        for b in self.__bases__:
            b.unsubscribe(self)
        
        # Register ourselves as a dependent of our bases
        self.__dict__['__bases__'] = bases
        for b in bases:
            b.subscribe(self)
        
        self.changed()

    __bases__ = property(
        
        lambda self: self.__dict__.get('__bases__', ()),
        __setBases,
        )

    def changed(self):
        """We, or something we depend on, have changed
        """

        implied = self._implied
        implied.clear()

        ancestors = ro(self)
        self.__sro__ = tuple(ancestors)
        self.__iro__ = tuple([ancestor for ancestor in ancestors
                              if isinstance(ancestor, InterfaceClass)
                             ])

        for ancestor in ancestors:
            # We directly imply our ancestors:
            implied[ancestor] = ()

        # Now, advise our dependents of change:
        for dependent in self.dependents.keys():
            dependent.changed()


    def interfaces(self):
        """Return an iterator for the interfaces in the specification

        for example::

          >>> from zope.interface import Interface
          >>> class I1(Interface): pass
          ...
          >>> class I2(I1): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(I3): pass
          ...
          >>> spec = Specification((I2, I3))
          >>> spec = Specification((I4, spec))
          >>> i = spec.interfaces()
          >>> i.next().getName()
          'I4'
          >>> i.next().getName()
          'I2'
          >>> i.next().getName()
          'I3'
          >>> list(i)
          []
        """
        seen = {}
        for base in self.__bases__:
            for interface in base.interfaces():
                if interface not in seen:
                    seen[interface] = 1
                    yield interface
        

    def extends(self, interface, strict=True):
        """Does the specification extend the given interface?

        Test whether an interface in the specification extends the
        given interface

        Examples::

          >>> from zope.interface import Interface
          >>> from zope.interface.declarations import Declaration
          >>> class I1(Interface): pass
          ...
          >>> class I2(I1): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(I3): pass
          ...
          >>> spec = Declaration()
          >>> int(spec.extends(Interface))
          0
          >>> spec = Declaration(I2)
          >>> int(spec.extends(Interface))
          1
          >>> int(spec.extends(I1))
          1
          >>> int(spec.extends(I2))
          1
          >>> int(spec.extends(I3))
          0
          >>> int(spec.extends(I4))
          0
          >>> I2.extends(I2)
          0
          >>> I2.extends(I2, False)
          1
          >>> I2.extends(I2, strict=False)
          1

        """
        return ((interface in self._implied)
                and
                ((not strict) or (self != interface))
                )

    def weakref(self, callback=None):
        if callback is None:
            return weakref.ref(self)
        else:
            return weakref.ref(self, callback)


    def get(self, name, default=None):
        """Query for an attribute description
        """
        try:
            attrs = self._v_attrs
        except AttributeError:
            attrs = self._v_attrs = {}
        attr = attrs.get(name)
        if attr is None:
            for iface in self.__iro__:
                attr = iface.direct(name)
                if attr is not None:
                    attrs[name] = attr
                    break
            
        if attr is None:
            return default
        else:
            return attr

class InterfaceClass(Element, Specification):
    """Prototype (scarecrow) Interfaces Implementation."""

    # We can't say this yet because we don't have enough
    # infrastructure in place.
    #
    #implements(IInterface)

    def __init__(self, name, bases=(), attrs=None, __doc__=None,
                 __module__=None):

        if __module__ is None:
            if (attrs is not None and
                ('__module__' in attrs) and
                isinstance(attrs['__module__'], str)
                ):
                __module__ = attrs['__module__']
                del attrs['__module__']
            else:

                try:
                    # Figure out what module defined the interface.
                    # This is how cPython figures out the module of
                    # a class, but of course it does it in C. :-/
                    __module__ = sys._getframe(1).f_globals['__name__']
                except (AttributeError, KeyError):
                    pass

        self.__module__ = __module__

        if attrs is None:
            attrs = {}

        d = attrs.get('__doc__')
        if d is not None:
            if not isinstance(d, Attribute):
                if __doc__ is None:
                    __doc__ = d
                del attrs['__doc__']

        if __doc__ is None:
            __doc__ = ''

        Element.__init__(self, name, __doc__)

        if attrs.has_key(TAGGED_DATA):
            tagged_data = attrs[TAGGED_DATA]
            del attrs[TAGGED_DATA]
        else:
            tagged_data = None
        if tagged_data is not None:
            for key, val in tagged_data.items():
                self.setTaggedValue(key, val)

        for base in bases:
            if not isinstance(base, InterfaceClass):
                raise TypeError, 'Expected base interfaces'

        Specification.__init__(self, bases)

        # Make sure that all recorded attributes (and methods) are of type
        # `Attribute` and `Method`
        for name, attr in attrs.items():
            if isinstance(attr, Attribute):
                attr.interface = self
                if not attr.__name__:
                    attr.__name__ = name
            elif isinstance(attr, FunctionType):
                attrs[name] = fromFunction(attr, self, name=name)
            elif attr is _decorator_non_return:
                del attrs[name]
            else:
                raise InvalidInterface("Concrete attribute, %s" %name)

        self.__attrs = attrs

        self.__identifier__ = "%s.%s" % (self.__module__, self.__name__)

    def interfaces(self):
        """Return an iterator for the interfaces in the specification

        for example::

          >>> from zope.interface import Interface
          >>> class I1(Interface): pass
          ...
          >>> 
          >>> i = I1.interfaces()
          >>> i.next().getName()
          'I1'
          >>> list(i)
          []
        """
        yield self



    def getBases(self):
        return self.__bases__

    def isEqualOrExtendedBy(self, other):
        """Same interface or extends?"""
        if self == other:
            return True
        return other.extends(self)

    def names(self, all=False):
        """Return the attribute names defined by the interface."""
        if not all:
            return self.__attrs.keys()

        r = {}
        for name in self.__attrs.keys():
            r[name] = 1
        for base in self.__bases__:
            for name in base.names(all):
                r[name] = 1
        return r.keys()

    def __iter__(self):
        return iter(self.names(all=True))

    def namesAndDescriptions(self, all=False):
        """Return attribute names and descriptions defined by interface."""
        if not all:
            return self.__attrs.items()

        r = {}
        for name, d in self.__attrs.items():
            r[name] = d

        for base in self.__bases__:
            for name, d in base.namesAndDescriptions(all):
                if name not in r:
                    r[name] = d

        return r.items()

    def getDescriptionFor(self, name):
        """Return the attribute description for the given name."""
        r = self.get(name)
        if r is not None:
            return r

        raise KeyError, name

    __getitem__ = getDescriptionFor

    def __contains__(self, name):
        return self.get(name) is not None

    def direct(self, name):
        return self.__attrs.get(name)

    def queryDescriptionFor(self, name, default=None):
        return self.get(name, default)

    def deferred(self):
        """Return a defered class corresponding to the interface."""
        if hasattr(self, "_deferred"): return self._deferred

        klass={}
        exec "class %s: pass" % self.__name__ in klass
        klass=klass[self.__name__]

        self.__d(klass.__dict__)

        self._deferred=klass

        return klass

    def validateInvariants(self, obj, errors=None):
        """validate object to defined invariants."""
        for call in self.queryTaggedValue('invariants', []):
            try:
                call(obj)
            except Invalid, e:
                if errors is None:
                    raise
                else:
                    errors.append(e)
        for base in self.__bases__:
            try:
                base.validateInvariants(obj, errors)
            except Invalid:
                if errors is None:
                    raise
                pass
        if errors:
            raise Invalid(errors)

    def _getInterface(self, ob, name):
        """Retrieve a named interface."""
        return None

    def __d(self, dict):

        for k, v in self.__attrs.items():
            if isinstance(v, Method) and not (k in dict):
                dict[k]=v

        for b in self.__bases__: b.__d(dict)

    def __repr__(self):
        r = getattr(self, '_v_repr', self)
        if r is self:
            name = self.__name__
            m = self.__module__
            if m:
                name = '%s.%s' % (m, name)
            r = "<%s %s>" % (self.__class__.__name__, name)
            self._v_repr = r
        return r

    def __call__():
        # TRICK! Create the call method
        #
        # An embedded function is used to allow an optional argument to
        # __call__ without resorting to a global marker.
        #
        # The evility of this trick is a reflection of the underlying
        # evility of "optional" arguments, arguments whose presense or
        # absense changes the behavior of the methods.
        # 
        # I think the evil is necessary, and perhaps desireable to
        # provide some consistencey with the PEP 246 adapt method.

        marker = object()
        
        def __call__(self, obj, alternate=marker):
            """Adapt an object to the interface

               The sematics based on those of the PEP 246 adapt function.

               If an object cannot be adapted, then a TypeError is raised::

                 >>> import zope.interface
                 >>> class I(zope.interface.Interface):
                 ...     pass

                 >>> I(0)
                 Traceback (most recent call last):
                 ...
                 TypeError: ('Could not adapt', 0, """ \
                      """<InterfaceClass zope.interface.interface.I>)

               unless an alternate value is provided as a second
               positional argument::

                 >>> I(0, 'bob')
                 'bob'

               If an object already implements the interface, then it will be
               returned::

                 >>> class C(object):
                 ...     zope.interface.implements(I)

                 >>> obj = C()
                 >>> I(obj) is obj
                 True

               If an object implements __conform__, then it will be used::

                 >>> class C(object):
                 ...     zope.interface.implements(I)
                 ...     def __conform__(self, proto):
                 ...          return 0

                 >>> I(C())
                 0

               Adapter hooks (see __adapt__) will also be used, if present:

                 >>> from zope.interface.interface import adapter_hooks
                 >>> def adapt_0_to_42(iface, obj):
                 ...     if obj == 0:
                 ...         return 42

                 >>> adapter_hooks.append(adapt_0_to_42)
                 >>> I(0)
                 42

                 >>> adapter_hooks.remove(adapt_0_to_42)
                 >>> I(0)
                 Traceback (most recent call last):
                 ...
                 TypeError: ('Could not adapt', 0, """ \
                      """<InterfaceClass zope.interface.interface.I>)

            """
            conform = getattr(obj, '__conform__', None)
            if conform is not None:
                try:
                    adapter = conform(self)
                except TypeError:
                    # We got a TypeError. It might be an error raised by
                    # the __conform__ implementation, or *we* may have
                    # made the TypeError by calling an unbound method
                    # (object is a class).  In the later case, we behave
                    # as though there is no __conform__ method. We can
                    # detect this case by checking whether there is more
                    # than one traceback object in the traceback chain:
                    if sys.exc_info()[2].tb_next is not None:
                        # There is more than one entry in the chain, so
                        # reraise the error:
                        raise
                    # This clever trick is from Phillip Eby
                else:
                    if adapter is not None:
                        return adapter

            adapter = self.__adapt__(obj)

            if adapter is None:
                if alternate is not marker:
                    return alternate
                
                raise TypeError("Could not adapt", obj, self)

            return adapter

        return __call__

    __call__ = __call__() # TRICK! Make the *real* __call__ method

    def __adapt__(self, obj):
        """Adapt an object to the reciever

           This method is normally not called directly. It is called by
           the PEP 246 adapt framework and by the interface __call__
           operator. 

           The adapt method is responsible for adapting an object to
           the reciever.

           The default version returns None::

             >>> import zope.interface
             >>> class I(zope.interface.Interface):
             ...     pass

             >>> I.__adapt__(0)

           unless the object given provides the interface::

             >>> class C(object):
             ...     zope.interface.implements(I)

             >>> obj = C()
             >>> I.__adapt__(obj) is obj
             True

           Adapter hooks can be provided (or removed) to provide custom
           adaptation. We'll install a silly hook that adapts 0 to 42.
           We install a hook by simply adding it to the adapter_hooks
           list::

             >>> from zope.interface.interface import adapter_hooks
             >>> def adapt_0_to_42(iface, obj):
             ...     if obj == 0:
             ...         return 42

             >>> adapter_hooks.append(adapt_0_to_42)
             >>> I.__adapt__(0)
             42

           Hooks must either return an adapter, or None if no adapter can
           be found.

           Hooks can be uninstalled by removing them from the list::

             >>> adapter_hooks.remove(adapt_0_to_42)
             >>> I.__adapt__(0)

           """
        if self.providedBy(obj):
            return obj

        for hook in adapter_hooks:
            adapter = hook(self, obj)
            if adapter is not None:
                return adapter

    def __reduce__(self):
        return self.__name__

    def __cmp(self, o1, o2):
        # Yes, I did mean to name this __cmp, rather than __cmp__.
        # It is a private method used by __lt__ and __gt__.
        # I don't want to override __eq__ because I want the default
        # __eq__, which is really fast.
        """Make interfaces sortable

        TODO: It would ne nice if:

           More specific interfaces should sort before less specific ones.
           Otherwise, sort on name and module.

           But this is too complicated, and we're going to punt on it
           for now.

        For now, sort on interface and module name.

        None is treated as a pseudo interface that implies the loosest
        contact possible, no contract. For that reason, all interfaces
        sort before None.

        """
        if o1 == o2:
            return 0

        if o1 is None:
            return 1
        if o2 is None:
            return -1


        n1 = (getattr(o1, '__name__', ''),
              getattr(getattr(o1,  '__module__', None), '__name__', ''))
        n2 = (getattr(o2, '__name__', ''),
              getattr(getattr(o2,  '__module__', None), '__name__', ''))

        return cmp(n1, n2)

    def __lt__(self, other):
        c = self.__cmp(self, other)
        #print '<', self, other, c < 0, c
        return c < 0

    def __gt__(self, other):
        c = self.__cmp(self, other)
        #print '>', self, other, c > 0, c
        return c > 0


adapter_hooks = []

Interface = InterfaceClass("Interface", __module__ = 'zope.interface')

class Attribute(Element):
    """Attribute descriptions
    """

    # We can't say this yet because we don't have enough
    # infrastructure in place.
    #
    # implements(IAttribute)

    interface = None


class Method(Attribute):
    """Method interfaces

    The idea here is that you have objects that describe methods.
    This provides an opportunity for rich meta-data.
    """

    # We can't say this yet because we don't have enough
    # infrastructure in place.
    #
    # implements(IMethod)

    def __call__(self, *args, **kw):
        raise BrokenImplementation(self.interface, self.__name__)

    def getSignatureInfo(self):
        return {'positional': self.positional,
                'required': self.required,
                'optional': self.optional,
                'varargs': self.varargs,
                'kwargs': self.kwargs,
                }

    def getSignatureString(self):
        sig = "("
        for v in self.positional:
            sig = sig + v
            if v in self.optional.keys():
                sig = sig + "=%s" % `self.optional[v]`
            sig = sig + ", "
        if self.varargs:
            sig = sig + ("*%s, " % self.varargs)
        if self.kwargs:
            sig = sig + ("**%s, " % self.kwargs)

        # slice off the last comma and space
        if self.positional or self.varargs or self.kwargs:
            sig = sig[:-2]

        sig = sig + ")"
        return sig


def fromFunction(func, interface=None, imlevel=0, name=None):
    name = name or func.__name__
    method = Method(name, func.__doc__)
    defaults = func.func_defaults or ()
    code = func.func_code
    # Number of positional arguments
    na = code.co_argcount-imlevel
    names = code.co_varnames[imlevel:]
    opt = {}
    # Number of required arguments
    nr = na-len(defaults)
    if nr < 0:
        defaults=defaults[-nr:]
        nr = 0

    # Determine the optional arguments.
    for i in range(len(defaults)):
        opt[names[i+nr]] = defaults[i]

    method.positional = names[:na]
    method.required = names[:nr]
    method.optional = opt

    argno = na

    # Determine the function's variable argument's name (i.e. *args)
    if code.co_flags & CO_VARARGS:
        method.varargs = names[argno]
        argno = argno + 1
    else:
        method.varargs = None

    # Determine the function's keyword argument's name (i.e. **kw)
    if code.co_flags & CO_VARKEYWORDS:
        method.kwargs = names[argno]
    else:
        method.kwargs = None

    method.interface = interface

    for key, value in func.__dict__.items():
        method.setTaggedValue(key, value)

    return method


def fromMethod(meth, interface=None, name=None):
    func = meth.im_func
    return fromFunction(func, interface, imlevel=1, name=name)


# Now we can create the interesting interfaces and wire them up:
def _wire():
    from zope.interface.declarations import classImplements

    from zope.interface.interfaces import IAttribute
    classImplements(Attribute, IAttribute)

    from zope.interface.interfaces import IMethod
    classImplements(Method, IMethod)

    from zope.interface.interfaces import IInterface
    classImplements(InterfaceClass, IInterface)

# We import this here to deal with module dependencies.
from zope.interface.declarations import providedBy, implementedBy
from zope.interface.exceptions import InvalidInterface
from zope.interface.exceptions import BrokenImplementation
