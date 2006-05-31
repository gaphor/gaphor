##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Implementation of interface declarations

There are three flavors of declarations:

  - Declarations are used to simply name declared interfaces.

  - ImplementsDeclarations are used to express the interfaces that a
    class implements (that instances of the class provides).

    Implements specifications support inheriting interfaces.

  - ProvidesDeclarations are used to express interfaces directly
    provided by objects.
    

$Id$
"""
__docformat__ = 'restructuredtext'
import sys
import weakref
from zope.interface.interface import InterfaceClass, Specification
from ro import mergeOrderings, ro
import exceptions
from types import ClassType
from zope.interface.advice import addClassAdvisor

# Registry of class-implementation specifications 
BuiltinImplementationSpecifications = {}

class Declaration(Specification):
    """Interface declarations

    """

    def __init__(self, *interfaces):
        Specification.__init__(self, _normalizeargs(interfaces))

    def changed(self):
        Specification.changed(self)
        try:
            del self._v_attrs
        except AttributeError:
            pass

    def __contains__(self, interface):
        """Test whether an interface is in the specification

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
          >>> spec = Declaration(I2, I3)
          >>> spec = Declaration(I4, spec)
          >>> int(I1 in spec)
          0
          >>> int(I2 in spec)
          1
          >>> int(I3 in spec)
          1
          >>> int(I4 in spec)
          1
        """
        return self.extends(interface) and interface in self.interfaces()

    def __iter__(self):
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
          >>> spec = Declaration(I2, I3)
          >>> spec = Declaration(I4, spec)
          >>> i = iter(spec)
          >>> i.next().getName()
          'I4'
          >>> i.next().getName()
          'I2'
          >>> i.next().getName()
          'I3'
          >>> list(i)
          []
        """
        return self.interfaces()

    def flattened(self):
        """Return an iterator of all included and extended interfaces

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
          >>> spec = Declaration(I2, I3)
          >>> spec = Declaration(I4, spec)
          >>> i = spec.flattened()
          >>> i.next().getName()
          'I4'
          >>> i.next().getName()
          'I2'
          >>> i.next().getName()
          'I1'
          >>> i.next().getName()
          'I3'
          >>> i.next().getName()
          'Interface'
          >>> list(i)
          []

        """
        return iter(self.__iro__)

    def __sub__(self, other):
        """Remove interfaces from a specification

        Examples::

          >>> from zope.interface import Interface
          >>> class I1(Interface): pass
          ...
          >>> class I2(I1): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(I3): pass
          ...
          >>> spec = Declaration()
          >>> [iface.getName() for iface in spec]
          []
          >>> spec -= I1
          >>> [iface.getName() for iface in spec]
          []
          >>> spec -= Declaration(I1, I2)
          >>> [iface.getName() for iface in spec]
          []
          >>> spec = Declaration(I2, I4)
          >>> [iface.getName() for iface in spec]
          ['I2', 'I4']
          >>> [iface.getName() for iface in spec - I4]
          ['I2']
          >>> [iface.getName() for iface in spec - I1]
          ['I4']
          >>> [iface.getName() for iface
          ...  in spec - Declaration(I3, I4)]
          ['I2']

        """

        return Declaration(
            *[i for i in self.interfaces()
                if not [j for j in other.interfaces()
                        if i.extends(j, 0)]
                ]
                )
    
    def __add__(self, other):
        """Add two specifications or a specification and an interface


        Examples::

          >>> from zope.interface import Interface
          >>> class I1(Interface): pass
          ...
          >>> class I2(I1): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(I3): pass
          ...
          >>> spec = Declaration()
          >>> [iface.getName() for iface in spec]
          []
          >>> [iface.getName() for iface in spec+I1]
          ['I1']
          >>> [iface.getName() for iface in I1+spec]
          ['I1']
          >>> spec2 = spec
          >>> spec += I1
          >>> [iface.getName() for iface in spec]
          ['I1']
          >>> [iface.getName() for iface in spec2]
          []
          >>> spec2 += Declaration(I3, I4)
          >>> [iface.getName() for iface in spec2]
          ['I3', 'I4']
          >>> [iface.getName() for iface in spec+spec2]
          ['I1', 'I3', 'I4']
          >>> [iface.getName() for iface in spec2+spec]
          ['I3', 'I4', 'I1']

        """

        seen = {}
        result = []
        for i in self.interfaces():
            if i not in seen:
                seen[i] = 1
                result.append(i)
        for i in other.interfaces():
            if i not in seen:
                seen[i] = 1
                result.append(i)

        return Declaration(*result)

    __radd__ = __add__

    def __nonzero__(self):
        """Test whether there are any interfaces in a specification.

        >>> from zope.interface import Interface
        >>> class I1(Interface): pass
        ...
        >>> spec = Declaration(I1)
        >>> int(bool(spec))
        1
        >>> spec = Declaration()
        >>> int(bool(spec))
        0
        """
        return bool(self.__iro__)


##############################################################################
#
# Implementation specifications
#
# These specify interfaces implemented by instances of classes

class Implements(Declaration):
    inherit = None
    declared = ()
    __name__ = '?'

    def __repr__(self):
        return '<implementedBy %s>' % (self.__name__)
    
        

def implementedByFallback(cls):
    """Return the interfaces implemented for a class' instances

      The value returned is an IDeclaration.

      for example:

        >>> from zope.interface import Interface
        >>> class I1(Interface): pass
        ...
        >>> class I2(I1): pass
        ...
        >>> class I3(Interface): pass
        ...
        >>> class I4(I3): pass
        ...
        >>> class C1(object):
        ...   implements(I2)
        >>> class C2(C1):
        ...   implements(I3)
        >>> [i.getName() for i in implementedBy(C2)]
        ['I3', 'I2']
      """

    # This also manages storage of implementation specifications

    try:
        spec = cls.__dict__.get('__implemented__')
    except AttributeError:
        
        # we can't get the class dict. This is probably due to a
        # security proxy.  If this is the case, then probably no
        # descriptor was installed for the class.

        # We don't want to depend directly on zope.security in
        # zope.interface, but we'll try to make reasonable
        # accommodations in an indirect way.

        # We'll check to see if there's an implements:

        spec = getattr(cls, '__implemented__', None)
        if spec is None:
            # There's no spec stred in the class. Maybe its a builtin:
            spec = BuiltinImplementationSpecifications.get(cls)
            if spec is not None:
                return spec
            return _empty
        
        if spec.__class__ == Implements:
            # we defaulted to _empty or there was a spec. Good enough.
            # Return it.
            return spec

        # TODO: need old style __implements__ compatibility?
        # Hm, there's an __implemented__, but it's not a spec. Must be
        # an old-style declaration. Just compute a spec for it
        return Declaration(*_normalizeargs((spec, )))
        
    if isinstance(spec, Implements):
        return spec

    if spec is None:
        spec = BuiltinImplementationSpecifications.get(cls)
        if spec is not None:
            return spec

    # TODO: need old style __implements__ compatibility?
    if spec is not None:
        # old-style __implemented__ = foo declaration
        spec = (spec, ) # tuplefy, as it might be just an int
        spec = Implements(*_normalizeargs(spec))
        spec.inherit = None    # old-style implies no inherit
        del cls.__implemented__ # get rid of the old-style declaration
    else:
        try:
            bases = cls.__bases__
        except AttributeError:
            if not callable(cls):
                raise TypeError("ImplementedBy called for non-factory", cls)
            bases = ()

        spec = Implements(*[implementedBy(c) for c in bases])
        spec.inherit = cls

    spec.__name__ = (getattr(cls, '__module__', '?') or '?') + \
                    '.' + cls.__name__

    try:
        cls.__implemented__ = spec
        if not hasattr(cls, '__providedBy__'):
            cls.__providedBy__ = objectSpecificationDescriptor

        if (isinstance(cls, DescriptorAwareMetaClasses)
            and
            '__provides__' not in cls.__dict__):
            # Make sure we get a __provides__ descriptor
            cls.__provides__ = ClassProvides(
                cls,
                getattr(cls, '__class__', type(cls)),
                )
                        
    except TypeError:
        if not isinstance(cls, type):
            raise TypeError("ImplementedBy called for non-type", cls)
        BuiltinImplementationSpecifications[cls] = spec

    return spec

implementedBy = implementedByFallback

def classImplementsOnly(cls, *interfaces):
    """Declare the only interfaces implemented by instances of a class

      The arguments after the class are one or more interfaces or
      interface specifications (IDeclaration objects).

      The interfaces given (including the interfaces in the
      specifications) replace any previous declarations.

      Consider the following example::

          >>> from zope.interface import Interface
          >>> class I1(Interface): pass
          ...
          >>> class I2(Interface): pass
          ...
          >>> class I3(Interface): pass
          ...
          >>> class I4(Interface): pass
          ...
          >>> class A(object):
          ...   implements(I3)
          >>> class B(object):
          ...   implements(I4)
          >>> class C(A, B):
          ...   pass
          >>> classImplementsOnly(C, I1, I2)
          >>> [i.getName() for i in implementedBy(C)]
          ['I1', 'I2']

      Instances of ``C`` provide only ``I1``, ``I2``, and regardless of
      whatever interfaces instances of ``A`` and ``B`` implement.

      """
    spec = implementedBy(cls)
    spec.__bases__ = tuple(_normalizeargs(interfaces))
    spec.inherit = None

def classImplements(cls, *interfaces):
    """Declare additional interfaces implemented for instances of a class

      The arguments after the class are one or more interfaces or
      interface specifications (IDeclaration objects).

      The interfaces given (including the interfaces in the
      specifications) are added to any interfaces previously
      declared.

      Consider the following example::


      for example:

      >>> from zope.interface import Interface
      >>> class I1(Interface): pass
      ...
      >>> class I2(Interface): pass
      ...
      >>> class I3(Interface): pass
      ...
      >>> class I4(Interface): pass
      ...
      >>> class I5(Interface): pass
      ...
      >>> class A(object):
      ...   implements(I3)
      >>> class B(object):
      ...   implements(I4)
      >>> class C(A, B):
      ...   pass
      >>> classImplements(C, I1, I2)
      >>> [i.getName() for i in implementedBy(C)]
      ['I1', 'I2', 'I3', 'I4']
      >>> classImplements(C, I5)
      >>> [i.getName() for i in implementedBy(C)]
      ['I1', 'I2', 'I5', 'I3', 'I4']

      Instances of ``C`` provide ``I1``, ``I2``, ``I5``, and whatever
      interfaces instances of ``A`` and ``B`` provide.

      """

    spec = implementedBy(cls)
    spec.declared += tuple(_normalizeargs(interfaces))

    # compute the bases
    bases = []
    seen = {}
    for b in spec.declared:
        if b not in seen:
            seen[b] = 1
            bases.append(b)

    if spec.inherit is not None:

        for c in spec.inherit.__bases__:
            b = implementedBy(c)
            if b not in seen:
                seen[b] = 1
                bases.append(b)
        
    spec.__bases__ = tuple(bases)

def _implements_advice(cls):
    interfaces, classImplements = cls.__dict__['__implements_advice_data__']
    del cls.__implements_advice_data__
    classImplements(cls, *interfaces)
    return cls


class implementer:

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, DescriptorAwareMetaClasses):
            raise TypeError("Can't use implementer with classes.  Use one of "
                            "the class-declaration functions instead."
                            )
        spec = Implements(*self.interfaces)
        try:
            ob.__implemented__ = spec
        except AttributeError:
            raise TypeError("Can't declare implements", ob)
        return ob

def _implements(name, interfaces, classImplements):
    frame = sys._getframe(2)
    locals = frame.f_locals

    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or (
        ('__module__' not in locals) and sys.version_info[:3] > (2, 2, 0)):
        raise TypeError(name+" can be used only from a class definition.")

    if '__implements_advice_data__' in locals:
        raise TypeError(name+" can be used only once in a class definition.")

    locals['__implements_advice_data__'] = interfaces, classImplements
    addClassAdvisor(_implements_advice, depth=3)

def implements(*interfaces):
    """Declare interfaces implemented by instances of a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface
      specifications (IDeclaration objects).

      The interfaces given (including the interfaces in the
      specifications) are added to any interfaces previously
      declared.

      Previous declarations include declarations for base classes
      unless implementsOnly was used.

      This function is provided for convenience. It provides a more
      convenient way to call classImplements. For example::

        implements(I1)

      is equivalent to calling::

        classImplements(C, I1)

      after the class has been created.

      Consider the following example::


        >>> from zope.interface import Interface
        >>> class IA1(Interface): pass
        ...
        >>> class IA2(Interface): pass
        ...
        >>> class IB(Interface): pass
        ...
        >>> class IC(Interface): pass
        ...
        >>> class A(object): implements(IA1, IA2)
        ...
        >>> class B(object): implements(IB)
        ...

        >>> class C(A, B):
        ...    implements(IC)

        >>> ob = C()
        >>> int(IA1 in providedBy(ob))
        1
        >>> int(IA2 in providedBy(ob))
        1
        >>> int(IB in providedBy(ob))
        1
        >>> int(IC in providedBy(ob))
        1

      Instances of ``C`` implement ``I1``, ``I2``, and whatever interfaces
      instances of ``A`` and ``B`` implement.

      """
    _implements("implements", interfaces, classImplements)

def implementsOnly(*interfaces):
    """Declare the only interfaces implemented by instances of a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface
      specifications (IDeclaration objects).

      Previous declarations including declarations for base classes
      are overridden.

      This function is provided for convenience. It provides a more
      convenient way to call classImplementsOnly. For example::

        implementsOnly(I1)

      is equivalent to calling::

        classImplementsOnly(I1)

      after the class has been created.

      Consider the following example::

        >>> from zope.interface import Interface
        >>> class IA1(Interface): pass
        ...
        >>> class IA2(Interface): pass
        ...
        >>> class IB(Interface): pass
        ...
        >>> class IC(Interface): pass
        ...
        >>> class A(object): implements(IA1, IA2)
        ...
        >>> class B(object): implements(IB)
        ...

        >>> class C(A, B):
        ...    implementsOnly(IC)

        >>> ob = C()
        >>> int(IA1 in providedBy(ob))
        0
        >>> int(IA2 in providedBy(ob))
        0
        >>> int(IB in providedBy(ob))
        0
        >>> int(IC in providedBy(ob))
        1


      Instances of ``C`` implement ``IC``, regardless of what
      instances of ``A`` and ``B`` implement.

      """
    _implements("implementsOnly", interfaces, classImplementsOnly)

##############################################################################
#
# Instance declarations

class Provides(Declaration):  # Really named ProvidesClass
    """Implement __provides__, the instance-specific specification

    When an object is pickled, we pickle the interfaces that it implements.
    """

    def __init__(self, cls, *interfaces):
        self.__args = (cls, ) + interfaces
        self._cls = cls
        Declaration.__init__(self, *(interfaces + (implementedBy(cls), )))

    def __reduce__(self):
        return Provides, self.__args

    __module__ = 'zope.interface'

    def __get__(self, inst, cls):
        """Make sure that a class __provides__ doesn't leak to an instance

        For example::

          >>> from zope.interface import Interface
          >>> class IFooFactory(Interface): pass
          ...
          
          >>> class C(object):
          ...   pass

          >>> C.__provides__ = ProvidesClass(C, IFooFactory)
          >>> [i.getName() for i in C.__provides__]
          ['IFooFactory']
          >>> getattr(C(), '__provides__', 0)
          0

        """
        if inst is None and cls is self._cls:
            # We were accessed through a class, so we are the class'
            # provides spec. Just return this object, but only if we are
            # being called on the same class that we were defined for:
            return self

        raise AttributeError, '__provides__'

ProvidesClass = Provides

# Registry of instance declarations
# This is a memory optimization to allow objects to share specifications.
InstanceDeclarations = weakref.WeakValueDictionary()

def Provides(*interfaces):
    """Cache instance declarations

      Instance declarations are shared among instances that have the
      same declaration.  The declarations are cached in a weak value
      dictionary.

      (Note that, in the examples below, we are going to make
       assertions about the size of the weakvalue dictionary.  For the
       assertions to be meaningful, we need to force garbage
       collection to make sure garbage objects are, indeed, removed
       from the system. Depending on how Python is run, we may need to
       make multiple calls to be sure.  We provide a collect function
       to help with this:

       >>> import gc
       >>> def collect():
       ...     for i in range(4):
       ...         gc.collect()

      )
      
      >>> collect()
      >>> before = len(InstanceDeclarations)

      >>> class C(object):
      ...    pass

      >>> from zope.interface import Interface
      >>> class I(Interface):
      ...    pass
      
      >>> c1 = C()
      >>> c2 = C()

      >>> len(InstanceDeclarations) == before
      1

      >>> directlyProvides(c1, I)
      >>> len(InstanceDeclarations) == before + 1
      1

      >>> directlyProvides(c2, I)
      >>> len(InstanceDeclarations) == before + 1
      1

      >>> del c1
      >>> collect()
      >>> len(InstanceDeclarations) == before + 1
      1

      >>> del c2
      >>> collect()
      >>> len(InstanceDeclarations) == before
      1
      
      """
    
    spec = InstanceDeclarations.get(interfaces)
    if spec is None:
        spec = ProvidesClass(*interfaces)
        InstanceDeclarations[interfaces] = spec

    return spec
Provides.__safe_for_unpickling__ = True


DescriptorAwareMetaClasses = ClassType, type
def directlyProvides(object, *interfaces):
    """Declare interfaces declared directly for an object

      The arguments after the object are one or more interfaces or
      interface specifications (IDeclaration objects).

      The interfaces given (including the interfaces in the
      specifications) replace interfaces previously
      declared for the object.

      Consider the following example::

        >>> from zope.interface import Interface
        >>> class I1(Interface): pass
        ...
        >>> class I2(Interface): pass
        ...
        >>> class IA1(Interface): pass
        ...
        >>> class IA2(Interface): pass
        ...
        >>> class IB(Interface): pass
        ...
        >>> class IC(Interface): pass
        ...
        >>> class A(object): implements(IA1, IA2)
        ...
        >>> class B(object): implements(IB)
        ...

        >>> class C(A, B):
        ...    implements(IC)

        >>> ob = C()
        >>> directlyProvides(ob, I1, I2)
        >>> int(I1 in providedBy(ob))
        1
        >>> int(I2 in providedBy(ob))
        1
        >>> int(IA1 in providedBy(ob))
        1
        >>> int(IA2 in providedBy(ob))
        1
        >>> int(IB in providedBy(ob))
        1
        >>> int(IC in providedBy(ob))
        1

      The object, ``ob`` provides ``I1``, ``I2``, and whatever interfaces
      instances have been declared for instances of ``C``.

      To remove directly provided interfaces, use ``directlyProvidedBy`` and
      subtract the unwanted interfaces. For example::

        >>> directlyProvides(ob, directlyProvidedBy(ob)-I2)
        >>> int(I1 in providedBy(ob))
        1
        >>> int(I2 in providedBy(ob))
        0

      removes I2 from the interfaces directly provided by
      ``ob``. The object, ``ob`` no longer directly provides ``I2``,
      although it might still provide ``I2`` if it's class
      implements ``I2``.

      To add directly provided interfaces, use ``directlyProvidedBy`` and
      include additional interfaces.  For example::

        >>> int(I2 in providedBy(ob))
        0
        >>> directlyProvides(ob, directlyProvidedBy(ob), I2)

      adds I2 to the interfaces directly provided by ob::

        >>> int(I2 in providedBy(ob))
        1

      """

    # We need to avoid setting this attribute on meta classes that
    # don't support descriptors.
    # We can do away with this check when we get rid of the old EC
    cls = getattr(object, '__class__', None)
    if cls is not None and getattr(cls,  '__class__', None) is cls:
        # It's a meta class (well, at least it it could be an extension class)
        if not isinstance(object, DescriptorAwareMetaClasses):
            raise TypeError("Attempt to make an interface declaration on a "
                            "non-descriptor-aware class")

    interfaces = _normalizeargs(interfaces)
    if cls is None:
        cls = type(object)

    issub = False
    for damc in DescriptorAwareMetaClasses:
        if issubclass(cls, damc):
            issub = True
            break
    if issub:
        # we have a class or type.  We'll use a special descriptor
        # that provides some extra caching
        object.__provides__ = ClassProvides(object, cls, *interfaces)
    else:
        object.__provides__ = Provides(cls, *interfaces)
        
    
def alsoProvides(object, *interfaces):
    """Declare interfaces declared directly for an object

      The arguments after the object are one or more interfaces or
      interface specifications (IDeclaration objects).

      The interfaces given (including the interfaces in the
      specifications) are added to the interfaces previously
      declared for the object.
      
      Consider the following example::

        >>> from zope.interface import Interface
        >>> class I1(Interface): pass
        ...
        >>> class I2(Interface): pass
        ...
        >>> class IA1(Interface): pass
        ...
        >>> class IA2(Interface): pass
        ...
        >>> class IB(Interface): pass
        ...
        >>> class IC(Interface): pass
        ...
        >>> class A(object): implements(IA1, IA2)
        ...
        >>> class B(object): implements(IB)
        ...

        >>> class C(A, B):
        ...    implements(IC)

        >>> ob = C()
        >>> directlyProvides(ob, I1)
        >>> int(I1 in providedBy(ob))
        1
        >>> int(I2 in providedBy(ob))
        0
        >>> int(IA1 in providedBy(ob))
        1
        >>> int(IA2 in providedBy(ob))
        1
        >>> int(IB in providedBy(ob))
        1
        >>> int(IC in providedBy(ob))
        1
        
        >>> alsoProvides(ob, I2)
        >>> int(I1 in providedBy(ob))
        1
        >>> int(I2 in providedBy(ob))
        1
        >>> int(IA1 in providedBy(ob))
        1
        >>> int(IA2 in providedBy(ob))
        1
        >>> int(IB in providedBy(ob))
        1
        >>> int(IC in providedBy(ob))
        1
        
      The object, ``ob`` provides ``I1``, ``I2``, and whatever interfaces
      instances have been declared for instances of ``C``. Notice that the
      alsoProvides just extends the provided interfaces.
    """
    directlyProvides(object, directlyProvidedBy(object), *interfaces)

class ClassProvidesBasePy(object):

    def __get__(self, inst, cls):
        if cls is self._cls:
            # We only work if called on the class we were defined for
            
            if inst is None:
                # We were accessed through a class, so we are the class'
                # provides spec. Just return this object as is:
                return self

            return self._implements

        raise AttributeError, '__provides__'

ClassProvidesBase = ClassProvidesBasePy

# Try to get C base:
try:
    import _zope_interface_coptimizations
except ImportError:
    pass
else:
    from _zope_interface_coptimizations import ClassProvidesBase


class ClassProvides(Declaration, ClassProvidesBase):
    """Special descriptor for class __provides__

    The descriptor caches the implementedBy info, so that
    we can get declarations for objects without instance-specific
    interfaces a bit quicker.

        For example::

          >>> from zope.interface import Interface
          >>> class IFooFactory(Interface):
          ...     pass
          >>> class IFoo(Interface):
          ...     pass
          >>> class C(object):
          ...     implements(IFoo)
          ...     classProvides(IFooFactory)
          >>> [i.getName() for i in C.__provides__]
          ['IFooFactory']

          >>> [i.getName() for i in C().__provides__]
          ['IFoo']

    
    """

    def __init__(self, cls, metacls, *interfaces):
        self._cls = cls
        self._implements = implementedBy(cls)
        self.__args = (cls, metacls, ) + interfaces
        Declaration.__init__(self, *(interfaces + (implementedBy(metacls), )))

    def __reduce__(self):
        return self.__class__, self.__args

    # Copy base-class method for speed
    __get__ = ClassProvidesBase.__get__

def directlyProvidedBy(object):
    """Return the interfaces directly provided by the given object

    The value returned is an IDeclaration.

    """
    provides = getattr(object, "__provides__", None)
    if (provides is None # no spec
        or
        # We might have gotten the implements spec, as an
        # optimization. If so, it's like having only one base, that we
        # lop off to exclude class-supplied declarations:
        isinstance(provides, Implements)
        ):
        return _empty

    # Strip off the class part of the spec:
    return Declaration(provides.__bases__[:-1])

def classProvides(*interfaces):
    """Declare interfaces provided directly by a class

      This function is called in a class definition.

      The arguments are one or more interfaces or interface
      specifications (IDeclaration objects).

      The given interfaces (including the interfaces in the
      specifications) are used to create the class's direct-object
      interface specification.  An error will be raised if the module
      class has an direct interface specification.  In other words, it is
      an error to call this function more than once in a class
      definition.

      Note that the given interfaces have nothing to do with the
      interfaces implemented by instances of the class.

      This function is provided for convenience. It provides a more
      convenient way to call directlyProvidedByProvides for a class. For
      example::

        classProvides(I1)

      is equivalent to calling::

        directlyProvides(theclass, I1)

      after the class has been created.

      For example::

            >>> from zope.interface import Interface
            >>> class IFoo(Interface): pass
            ...
            >>> class IFooFactory(Interface): pass
            ...
            >>> class C(object):
            ...   implements(IFoo)
            ...   classProvides(IFooFactory)
            >>> [i.getName() for i in C.__providedBy__]
            ['IFooFactory']
            >>> [i.getName() for i in C().__providedBy__]
            ['IFoo']

      if equivalent to::

            >>> from zope.interface import Interface
            >>> class IFoo(Interface): pass
            ...
            >>> class IFooFactory(Interface): pass
            ...
            >>> class C(object):
            ...   implements(IFoo)
            >>> directlyProvides(C, IFooFactory)
            >>> [i.getName() for i in C.__providedBy__]
            ['IFooFactory']
            >>> [i.getName() for i in C().__providedBy__]
            ['IFoo']


      """
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a class def
    if (locals is frame.f_globals) or ('__module__' not in locals):
        raise TypeError(name+" can be used only from a class definition.")

    if '__provides__' in locals:
        raise TypeError(
            "classProvides can only be used once in a class definition.")

    locals["__provides__"] = _normalizeargs(interfaces)

    addClassAdvisor(_classProvides_advice, depth=2)

def _classProvides_advice(cls):
    interfaces = cls.__dict__['__provides__']
    del cls.__provides__
    directlyProvides(cls, *interfaces)
    return cls

def moduleProvides(*interfaces):
    """Declare interfaces provided by a module

    This function is used in a module definition.

    The arguments are one or more interfaces or interface
    specifications (IDeclaration objects).

    The given interfaces (including the interfaces in the
    specifications) are used to create the module's direct-object
    interface specification.  An error will be raised if the module
    already has an interface specification.  In other words, it is
    an error to call this function more than once in a module
    definition.

    This function is provided for convenience. It provides a more
    convenient way to call directlyProvides. For example::

      moduleImplements(I1)

    is equivalent to::

      directlyProvides(sys.modules[__name__], I1)

    """
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a class def
    if (locals is not frame.f_globals) or ('__name__' not in locals):
        raise TypeError(
            "moduleProvides can only be used from a module definition.")

    if '__provides__' in locals:
        raise TypeError(
            "moduleProvides can only be used once in a module definition.")

    module = sys.modules[__name__]

    locals["__provides__"] = Provides(type(module),
                                      *_normalizeargs(interfaces))

##############################################################################
#
# Declaration querying support

def ObjectSpecification(direct, cls):
    """Provide object specifications

    These combine information for the object and for it's classes.

    For example::

        >>> from zope.interface import Interface
        >>> class I1(Interface): pass
        ...
        >>> class I2(Interface): pass
        ...
        >>> class I3(Interface): pass
        ...
        >>> class I31(I3): pass
        ...
        >>> class I4(Interface): pass
        ...
        >>> class I5(Interface): pass
        ...
        >>> class A(object): implements(I1)
        ...
        >>> class B(object): __implemented__ = I2
        ...
        >>> class C(A, B): implements(I31)
        ...
        >>> c = C()
        >>> directlyProvides(c, I4)
        >>> [i.getName() for i in providedBy(c)]
        ['I4', 'I31', 'I1', 'I2']
        >>> [i.getName() for i in providedBy(c).flattened()]
        ['I4', 'I31', 'I3', 'I1', 'I2', 'Interface']
        >>> int(I1 in providedBy(c))
        1
        >>> int(I3 in providedBy(c))
        0
        >>> int(providedBy(c).extends(I3))
        1
        >>> int(providedBy(c).extends(I31))
        1
        >>> int(providedBy(c).extends(I5))
        0
        >>> class COnly(A, B): implementsOnly(I31)
        ...
        >>> class D(COnly): implements(I5)
        ...
        >>> c = D()
        >>> directlyProvides(c, I4)
        >>> [i.getName() for i in providedBy(c)]
        ['I4', 'I5', 'I31']
        >>> [i.getName() for i in providedBy(c).flattened()]
        ['I4', 'I5', 'I31', 'I3', 'Interface']
        >>> int(I1 in providedBy(c))
        0
        >>> int(I3 in providedBy(c))
        0
        >>> int(providedBy(c).extends(I3))
        1
        >>> int(providedBy(c).extends(I1))
        0
        >>> int(providedBy(c).extends(I31))
        1
        >>> int(providedBy(c).extends(I5))
        1


        nonzero:

        >>> from zope.interface import Interface
        >>> class I1(Interface):
        ...     pass
        >>> class I2(Interface):
        ...     pass
        >>> class C(object):
        ...     implements(I1)
        >>> c = C()
        >>> int(bool(providedBy(c)))
        1
        >>> directlyProvides(c, I2)
        >>> int(bool(providedBy(c)))
        1
        >>> class C(object):
        ...     pass
        >>> c = C()
        >>> int(bool(providedBy(c)))
        0
        >>> directlyProvides(c, I2)
        >>> int(bool(providedBy(c)))
        1


    """

    return Provides(cls, direct)

def getObjectSpecification(ob):

    provides = getattr(ob, '__provides__', None)
    if provides is not None:
        return provides
    
    try:
        cls = ob.__class__
    except AttributeError:
        # We can't get the class, so just consider provides
        return _empty

    return implementedBy(cls)

def providedBy(ob):

    # Here we have either a special object, an old-style declaration
    # or a descriptor

    # Try to get __providedBy__
    try:
        r = ob.__providedBy__
    except AttributeError:
        # Not set yet. Fall back to lower-level thing that computes it
        return getObjectSpecification(ob)
    

    try:
        # We might have gotten a descriptor from an instance of a
        # class (like an ExtensionClass) that doesn't support
        # descriptors.  We'll make sure we got one by trying to get
        # the only attribute, which all specs have.
        r.extends

    except AttributeError:

        # The object's class doesn't understand descriptors.
        # Sigh. We need to get an object descriptor, but we have to be
        # careful.  We want to use the instance's __provides__, if
        # there is one, but only if it didn't come from the class.

        try:
            r = ob.__provides__
        except AttributeError:
            # No __provides__, so just fall back to implementedBy
            return implementedBy(ob.__class__)

        # We need to make sure we got the __provides__ from the
        # instance. We'll do this by making sure we don't get the same
        # thing from the class:

        try:
            cp = ob.__class__.__provides__
        except AttributeError:
            # The ob doesn't have a class or the class has no
            # provides, assume we're done:
            return r

        if r is cp:
            # Oops, we got the provides from the class. This means
            # the object doesn't have it's own. We should use implementedBy
            return implementedBy(ob.__class__)

    return r

class ObjectSpecificationDescriptorPy(object):
    """Implement the __providedBy__ attribute

    The __providedBy__ attribute computes the interfaces peovided by
    an object.
    """

    def __get__(self, inst, cls):
        """Get an object specification for an object

        For example::

          >>> from zope.interface import Interface
          >>> class IFoo(Interface): pass
          ...
          >>> class IFooFactory(Interface): pass
          ...
          >>> class C(object):
          ...   implements(IFoo)
          ...   classProvides(IFooFactory)
          >>> [i.getName() for i in C.__providedBy__]
          ['IFooFactory']
          >>> [i.getName() for i in C().__providedBy__]
          ['IFoo']

        """

        # Get an ObjectSpecification bound to either an instance or a class,
        # depending on how we were accessed.
        
        if inst is None:
            return getObjectSpecification(cls)

        provides = getattr(inst, '__provides__', None)
        if provides is not None:
            return provides

        return implementedBy(cls)

ObjectSpecificationDescriptor = ObjectSpecificationDescriptorPy

##############################################################################

def _normalizeargs(sequence, output = None):
    """Normalize declaration arguments

    Normalization arguments might contain Declarions, tuples, or single
    interfaces.

    Anything but individial interfaces or implements specs will be expanded.
    """
    if output is None:
        output = []

    cls = sequence.__class__
    if InterfaceClass in cls.__mro__ or Implements in cls.__mro__:
        output.append(sequence)
    else:
        for v in sequence:
            _normalizeargs(v, output)
            
    return output

_empty = Declaration()

try:
    import _zope_interface_coptimizations
except ImportError:
    pass
else:
    from _zope_interface_coptimizations import implementedBy, providedBy
    from _zope_interface_coptimizations import getObjectSpecification
    from _zope_interface_coptimizations import ObjectSpecificationDescriptor

objectSpecificationDescriptor = ObjectSpecificationDescriptor()
    
