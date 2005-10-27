##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interface Package Interfaces

$Id$
"""
__docformat__ = 'restructuredtext'


from zope.interface import Interface
from zope.interface.interface import Attribute

class IElement(Interface):
    """Objects that have basic documentation and tagged values.
    """

    __name__ = Attribute('__name__', 'The object name')
    __doc__  = Attribute('__doc__', 'The object doc string')

    def getTaggedValue(tag):
        """Returns the value associated with 'tag'.

        Raise a KeyError of the tag isn't set
        """

    def queryTaggedValue(tag, default=None):
        """Returns the value associated with 'tag'.

        Return the default value of the tag isn't set.
        """

    def getTaggedValueTags():
        """Returns a list of all tags."""

    def setTaggedValue(tag, value):
        """Associates 'value' with 'key'."""


class IAttribute(IElement):
    """Attribute descriptors"""

    interface = Attribute('interface',
                          'Stores the interface instance in which the '
                          'attribute is located.')


class IMethod(IAttribute):
    """Method attributes
    """

    def getSignatureInfo():
        """Returns the signature information.

        This method returns a dictionary with the following keys:

        o `positional` - All positional arguments.

        o `required` - A list of all required arguments.

        o `optional` - A list of all optional arguments.

        o `varargs' - The name of the varargs argument.

        o `kwargs` - The name of the kwargs argument.
        """

    def getSignatureString():
        """Return a signature string suitable for inclusion in documentation.

        This method returns the function signature string. For example, if you
        have `func(a, b, c=1, d='f')`, then the signature string is `(a, b,
        c=1, d='f')`.
        """

class ISpecification(Interface):
    """Object Behavioral specifications
    """

    def extends(other, strict=True):
        """Test whether a specification extends another

        The specification extends other if it has other as a base
        interface or if one of it's bases extends other.

        If strict is false, then the specification extends itself.
        
        """

    def isOrExtends(other):
        """Test whether the specification is or extends another
        """

    def weakref(callback=None):
        """Return a weakref to the specification

        This method is, regrettably, needed to allow weakrefs to be
        computed to security-proxied specifications.  While the
        zope.interface package does not require zope.security or
        zope.proxy, it has to be able to coexist with it.

        """

    __bases__ = Attribute("""Base specifications

    A tuple if specifications from which this specification is
    directly derived.

    """)

    __sro__ = Attribute("""Specification-resolution order

    A tuple of the specification and all of it's ancestor
    specifications from most specific to least specific.

    (This is similar to the method-resolution order for new-style classes.)
    """)

    def get(name, default=None):
        """Look up the description for a name

        If the named attribute is not defined, the default is
        returned.
        """

        
class IInterface(ISpecification, IElement):
    """Interface objects

    Interface objects describe the behavior of an object by containing
    useful information about the object.  This information includes:

      o Prose documentation about the object.  In Python terms, this
        is called the "doc string" of the interface.  In this element,
        you describe how the object works in prose language and any
        other useful information about the object.

      o Descriptions of attributes.  Attribute descriptions include
        the name of the attribute and prose documentation describing
        the attributes usage.

      o Descriptions of methods.  Method descriptions can include:

        o Prose "doc string" documentation about the method and its
          usage.

        o A description of the methods arguments; how many arguments
          are expected, optional arguments and their default values,
          the position or arguments in the signature, whether the
          method accepts arbitrary arguments and whether the method
          accepts arbitrary keyword arguments.

      o Optional tagged data.  Interface objects (and their attributes and
        methods) can have optional, application specific tagged data
        associated with them.  Examples uses for this are examples,
        security assertions, pre/post conditions, and other possible
        information you may want to associate with an Interface or its
        attributes.

    Not all of this information is mandatory.  For example, you may
    only want the methods of your interface to have prose
    documentation and not describe the arguments of the method in
    exact detail.  Interface objects are flexible and let you give or
    take any of these components.

    Interfaces are created with the Python class statement using
    either Interface.Interface or another interface, as in::

      from zope.interface import Interface

      class IMyInterface(Interface):
        '''Interface documentation
        '''

        def meth(arg1, arg2):
            '''Documentation for meth
            '''

        # Note that there is no self argument

     class IMySubInterface(IMyInterface):
        '''Interface documentation
        '''

        def meth2():
            '''Documentation for meth2
            '''

    You use interfaces in two ways:

    o You assert that your object implement the interfaces.

      There are several ways that you can assert that an object
      implements an interface::

      1. Call zope.interface.implements in your class definition.

      2. Call zope.interfaces.directlyProvides on your object.

      3. Call 'zope.interface.classImplements' to assert that instances
         of a class implement an interface.

         For example::

           from zope.interface import classImplements

           classImplements(some_class, some_interface)

         This approach is useful when it is not an option to modify
         the class source.  Note that this doesn't affect what the
         class itself implements, but only what its instances
         implement.

    o You query interface meta-data. See the IInterface methods and
      attributes for details.

    """

    def providedBy(object):
        """Test whether the interface is implemented by the object

        Return true of the object asserts that it implements the
        interface, including asserting that it implements an extended
        interface.
        """

    def implementedBy(class_):
        """Test whether the interface is implemented by instances of the class

        Return true of the class asserts that its instances implement the
        interface, including asserting that they implement an extended
        interface.
        """

    def names(all=False):
        """Get the interface attribute names

        Return a sequence of the names of the attributes, including
        methods, included in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by base classes will be included.
        """

    def namesAndDescriptions(all=False):
        """Get the interface attribute names and descriptions

        Return a sequence of the names and descriptions of the
        attributes, including methods, as name-value pairs, included
        in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by base classes will be included.
        """

    def __getitem__(name):
        """Get the description for a name

        If the named attribute is not defined, a KeyError is raised.
        """

    def direct(name):
        """Get the description for the name if it was defined by the interface

        If the interface doesn't define the name, returns None.
        """
    
    def validateInvariants(obj, errors=None):
        """Validate invariants

        Validate object to defined invariants.  If errors is None,
        raises first Invalid error; if errors is a list, appends all errors
        to list, then raises Invalid with the errors as the first element
        of the "args" tuple."""

    def __contains__(name):
        """Test whether the name is defined by the interface"""

    def __iter__():
        """Return an iterator over the names defined by the interface

        The names iterated include all of the names defined by the
        interface directly and indirectly by base interfaces.
        """

    __module__ = Attribute("""The name of the module defining the interface""")

class IDeclaration(ISpecification):
    """Interface declaration

    Declarations are used to express the interfaces implemented by
    classes or provided by objects.
    
    """

    def __contains__(interface):
        """Test whether an interface is in the specification

        Return true if the given interface is one of the interfaces in
        the specification and false otherwise.
        """

    def __iter__():
        """Return an iterator for the interfaces in the specification
        """

    def flattened():
        """Return an iterator of all included and extended interfaces

        An iterator is returned for all interfaces either included in
        or extended by interfaces included in the specifications
        without duplicates. The interfaces are in "interface
        resolution order". The interface resolution order is such that
        base interfaces are listed after interfaces that extend them
        and, otherwise, interfaces are included in the order that they
        were defined in the specification.
        """

    def __sub__(interfaces):
        """Create an interface specification with some interfaces excluded

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are subtracted from the interface specification.

        Removing an interface that is not in the specification does
        not raise an error. Doing so has no effect.

        Removing an interface also removes sub-interfaces of the interface.

        """

    def __add__(interfaces):
        """Create an interface specification with some interfaces added

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are added to the interface specification.

        Adding an interface that is already in the specification does
        not raise an error. Doing so has no effect.
        """

    def __nonzero__():
        """Return a true value of the interface specification is non-empty
        """

class IInterfaceDeclaration(Interface):
    """Declare and check the interfaces of objects

    The functions defined in this interface are used to declare the
    interfaces that objects provide and to query the interfaces that have
    been declared.

    Interfaces can be declared for objects in two ways:

    - Interfaces are declared for instances of the object's class

    - Interfaces are declared for the object directly.

    The interfaces declared for an object are, therefore, the union of
    interfaces declared for the object directly and the interfaces
    declared for instances of the object's class.

    Note that we say that a class implements the interfaces provided
    by it's instances.  An instance can also provide interfaces
    directly.  The interfaces provided by an object are the union of
    the interfaces provided directly and the interfaces implemented by
    the class.
    """

    def providedBy(ob):
        """Return the interfaces provided by an object

        This is the union of the interfaces directly provided by an
        object and interfaces implemented by it's class.

        The value returned is an IDeclaration.
        """

    def implementedBy(class_):
        """Return the interfaces implemented for a class' instances

        The value returned is an IDeclaration.
        """

    def classImplements(class_, *interfaces):
        """Declare additional interfaces implemented for instances of a class

        The arguments after the class are one or more interfaces or
        interface specifications (IDeclaration objects).

        The interfaces given (including the interfaces in the
        specifications) are added to any interfaces previously
        declared.

        Consider the following example::

          class C(A, B):
             ...

          classImplements(C, I1, I2)


        Instances of ``C`` provide ``I1``, ``I2``, and whatever interfaces
        instances of ``A`` and ``B`` provide.
        """

    def implementer(*interfaces):
        """Create a decorator for declaring interfaces implemented by a facory

        A callable is returned that makes an implements declaration on
        objects passed to it.
        
        """

    def classImplementsOnly(class_, *interfaces):
        """Declare the only interfaces implemented by instances of a class

        The arguments after the class are one or more interfaces or
        interface specifications (IDeclaration objects).

        The interfaces given (including the interfaces in the
        specifications) replace any previous declarations.

        Consider the following example::

          class C(A, B):
             ...

          classImplements(C, IA, IB. IC)
          classImplementsOnly(C. I1, I2)

        Instances of ``C`` provide only ``I1``, ``I2``, and regardless of
        whatever interfaces instances of ``A`` and ``B`` implement.
        """

    def directlyProvidedBy(object):
        """Return the interfaces directly provided by the given object

        The value returned is an IDeclaration.
        """

    def directlyProvides(object, *interfaces):
        """Declare interfaces declared directly for an object

        The arguments after the object are one or more interfaces or
        interface specifications (IDeclaration objects).

        The interfaces given (including the interfaces in the
        specifications) replace interfaces previously
        declared for the object.

        Consider the following example::

          class C(A, B):
             ...

          ob = C()
          directlyProvides(ob, I1, I2)

        The object, ``ob`` provides ``I1``, ``I2``, and whatever interfaces
        instances have been declared for instances of ``C``.

        To remove directly provided interfaces, use ``directlyProvidedBy`` and
        subtract the unwanted interfaces. For example::

          directlyProvides(ob, directlyProvidedBy(ob)-I2)

        removes I2 from the interfaces directly provided by
        ``ob``. The object, ``ob`` no longer directly provides ``I2``,
        although it might still provide ``I2`` if it's class
        implements ``I2``.

        To add directly provided interfaces, use ``directlyProvidedBy`` and
        include additional interfaces.  For example::

          directlyProvides(ob, directlyProvidedBy(ob), I2)

        adds I2 to the interfaces directly provided by ob.
        """

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

          class C(A, B):
            implements(I1, I2)


        Instances of ``C`` implement ``I1``, ``I2``, and whatever interfaces
        instances of ``A`` and ``B`` implement.
        """

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

          class C(A, B):
            implementsOnly(I1, I2)


        Instances of ``C`` implement ``I1``, ``I2``, regardless of what
        instances of ``A`` and ``B`` implement.
        """

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
        convenient way to call directlyProvides for a class. For example::

          classProvides(I1)

        is equivalent to calling::

          directlyProvides(theclass, I1)

        after the class has been created.
        """

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
        convenient way to call directlyProvides for a module. For example::

          moduleImplements(I1)

        is equivalent to::

          directlyProvides(sys.modules[__name__], I1)
        """

    def Declaration(*interfaces):
        """Create an interface specification

        The arguments are one or more interfaces or interface
        specifications (IDeclaration objects).

        A new interface specification (IDeclaration) with
        the given interfaces is returned.
        """

class IAdapterRegistry(Interface):
    """Provide an interface-based registry for adapters

    This registry registers objects that are in some sense "from" a
    sequence of specification to an interface and a name.

    No specific semantics are assumed for the registered objects,
    however, the most common application will be to register factories
    that adapt objects providing required specifications to a provided
    interface. 
    
    """

    def register(required, provided, name, value):
        """Register a value

        A value is registered for a *sequence* of required specifications, a
        provided interface, and a name.
        """

    def lookup(required, provided, name, default=None):
        """Lookup a value

        A value is looked up based on a *sequence* of required
        specifications, a provided interface, and a name.
        """

    def lookupAll(required, provided):
        """Find all adapters from the required to the provided interfaces

        An iterable object is returned that provides name-value two-tuples.
        """

    def names(required, provided):
        """Return the names for which there are registered objects
        """

    def subscribe(required, provided, subscriber):
        """Register a subscriber

        A subscriber is registered for a *sequence* of required
        specifications, a provided interface, and a name.

        Multiple subscribers may be registered for the same (or
        equivalent) interfaces.
        """

    def subscriptions(required, provided):
        """Get a sequence of subscribers

        Subscribers for a *sequence* of required interfaces, and a provided
        interface are returned.
        """
    
