==========
Interfaces
==========

.. contents::

Interfaces are objects that specify (document) the external behavior
of objects that "provide" them.  An interface specifies behavior
through:

- Informal documentation in a doc string

- Attribute definitions

- Invariants, which are conditions that must hold for objects that
  provide the interface

Attribute definitions specify specific attributes. They define the
attribute name and provide documentation and constraints of attribute
values.  Attribute definitions can take a number of forms, as we'll
see below.

Defining interfaces
===================

Interfaces are defined using Python class statements:

  >>> import zope.interface
  >>> class IFoo(zope.interface.Interface):
  ...    """Foo blah blah"""
  ...
  ...    x = zope.interface.Attribute("""X blah blah""")
  ...
  ...    def bar(q, r=None):
  ...        """bar blah blah"""

In the example above, we've created an interface, `IFoo`.  We
subclassed `zope.interface.Interface`, which is an ancestor interface for
all interfaces, much as `object` is an ancestor of all new-style
classes [#create]_.   The interface is not a class, it's an Interface,
an instance of `InterfaceClass`::

  >>> type(IFoo)
  <class 'zope.interface.interface.InterfaceClass'>

We can ask for the interface's documentation::

  >>> IFoo.__doc__
  'Foo blah blah'

and its name::

  >>> IFoo.__name__
  'IFoo'

and even its module::

  >>> IFoo.__module__
  '__main__'

The interface defined two attributes:

`x`
  This is the simplest form of attribute definition.  It has a name
  and a doc string.  It doesn't formally specify anything else.

`bar`
  This is a method.  A method is defined via a function definition.  A
  method is simply an attribute constrained to be a callable with a
  particular signature, as provided by the function definition.

  Note that `bar` doesn't take a `self` argument.  Interfaces document
  how an object is *used*.  When calling instance methods, you don't
  pass a `self` argument, so a `self` argument isn't included in the
  interface signature.  The `self` argument in instance methods is
  really an implementation detail of Python instances. Other objects,
  besides instances can provide interfaces and their methods might not
  be instance methods. For example, modules can provide interfaces and
  their methods are usually just functions.  Even instances can have
  methods that are not instance methods.

You can access the attributes defined by an interface using mapping
syntax::

  >>> x = IFoo['x']
  >>> type(x)
  <class 'zope.interface.interface.Attribute'>
  >>> x.__name__
  'x'
  >>> x.__doc__
  'X blah blah'

  >>> IFoo.get('x').__name__
  'x'

  >>> IFoo.get('y')

You can use `in` to determine if an interface defines a name::

  >>> 'x' in IFoo
  True

You can iterate over interfaces to get the names they define::

  >>> names = list(IFoo)
  >>> names.sort()
  >>> names
  ['bar', 'x']

Remember that interfaces aren't classes. You can't access attribute
definitions as attributes of interfaces::

  >>> IFoo.x
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  AttributeError: 'InterfaceClass' object has no attribute 'x'

Methods provide access to the method signature::

  >>> bar = IFoo['bar']
  >>> bar.getSignatureString()
  '(q, r=None)'

TODO
  Methods really should have a better API.  This is something that
  needs to be improved.

Declaring interfaces
====================

Having defined interfaces, we can *declare* that objects provide
them.  Before we describe the details, lets define some some terms:

*provide*
   We say that objects *provide* interfaces.  If an object provides an
   interface, then the interface specifies the behavior of the
   object. In other words, interfaces specify the behavior of the
   objects that provide them.

*implement*
   We normally say that classes *implement* interfaces.  If a class
   implements an interface, then the instances of the class provide
   the interface.  Objects provide interfaces that their classes
   implement [#factory]_.  (Objects can provide interfaces directly,
   in addition to what their classes implement.)

   It is important to note that classes don't usually provide the
   interfaces that the implement.

   We can generalize this to factories.  For any callable object we
   can declare that it produces objects that provides some interfaces
   by saying that the factory implements the interfaces.

Now that we've defined these terms, we can talk about the API for
declaring interfaces.

Declaring implemented interfaces
--------------------------------

The most common way to declare interfaces is using the implements
function in a class statement::

  >>> class Foo:
  ...     zope.interface.implements(IFoo)
  ...
  ...     def __init__(self, x=None):
  ...         self.x = x
  ...
  ...     def bar(self, q, r=None):
  ...         return q, r, self.x
  ...
  ...     def __repr__(self):
  ...         return "Foo(%s)" % self.x


In this example, we declared that `Foo` implements `IFoo`. This means
that instances of `Foo` provide `IFoo`.  Having made this declaration,
there are several ways we can introspect the declarations.  First, we
can ask an interface whether it is implemented by a class::

  >>> IFoo.implementedBy(Foo)
  True

And we can ask whether an interface is provided by an object::

  >>> foo = Foo()
  >>> IFoo.providedBy(foo)
  True

Of course, `Foo` doesn't provide `IFoo`, it implements it::

  >>> IFoo.providedBy(Foo)
  False

We can also ask what interfaces are implemented by an object::

  >>> list(zope.interface.implementedBy(Foo))
  [<InterfaceClass __main__.IFoo>]

It's an error to ask for interfaces implemented by a non-callable
object::

  >>> IFoo.implementedBy(foo)
  Traceback (most recent call last):
  ...
  TypeError: ('ImplementedBy called for non-factory', Foo(None))

  >>> list(zope.interface.implementedBy(foo))
  Traceback (most recent call last):
  ...
  TypeError: ('ImplementedBy called for non-factory', Foo(None))

Similarly, we can ask what interfaces are provided by an object::

  >>> list(zope.interface.providedBy(foo))
  [<InterfaceClass __main__.IFoo>]
  >>> list(zope.interface.providedBy(Foo))
  []

We can declare interfaces implemented by other factories (besides
classes).  We do this using a Python-2.4-style decorator named
`implementer`.  In versions of Python before 2.4, this looks like:


  >>> def yfoo(y):
  ...     foo = Foo()
  ...     foo.y = y
  ...     return foo
  >>> yfoo = zope.interface.implementer(IFoo)(yfoo)

  >>> list(zope.interface.implementedBy(yfoo))
  [<InterfaceClass __main__.IFoo>]

Note that the implementer decorator may modify it's argument. Callers
should not assume that a new object is created.

Also note that, at least for now, implementer can't be used with
classes:

  >>> zope.interface.implementer(IFoo)(Foo)
  ... # doctest: +NORMALIZE_WHITESPACE
  Traceback (most recent call last):
    ...
  TypeError: Can't use implementer with classes.  
  Use one of the class-declaration functions instead.

Declaring provided interfaces
-----------------------------

We can declare interfaces directly provided by objects.  Suppose that
we want to document what the `__init__` method of the `Foo` class
does.  It's not *really* part of `IFoo`.  You wouldn't normally call
the `__init__` method on Foo instances.  Rather, the `__init__` method
is part of the `Foo`'s `__call__` method::

  >>> class IFooFactory(zope.interface.Interface):
  ...     """Create foos"""
  ...
  ...     def __call__(x=None):
  ...         """Create a foo
  ...
  ...         The argument provides the initial value for x ...
  ...         """

It's the class that provides this interface, so we declare the
interface on the class::

  >>> zope.interface.directlyProvides(Foo, IFooFactory)

And then, we'll see that Foo provides some interfaces::

  >>> list(zope.interface.providedBy(Foo))
  [<InterfaceClass __main__.IFooFactory>]
  >>> IFooFactory.providedBy(Foo)
  True

Declaring class interfaces is common enough that there's a special
declaration function for it, `classProvides`, that allows the
declaration from within a class statement::

  >>> class Foo2:
  ...     zope.interface.implements(IFoo)
  ...     zope.interface.classProvides(IFooFactory)
  ...
  ...     def __init__(self, x=None):
  ...         self.x = x
  ...
  ...     def bar(self, q, r=None):
  ...         return q, r, self.x
  ...
  ...     def __repr__(self):
  ...         return "Foo(%s)" % self.x

  >>> list(zope.interface.providedBy(Foo2))
  [<InterfaceClass __main__.IFooFactory>]
  >>> IFooFactory.providedBy(Foo2)
  True

There's a similar function, `moduleProvides`, that supports interface
declarations from within module definitions.  For example, see the use
of `moduleProvides` call in `zope.interface.__init__`, which declares that
the package `zope.interface` provides `IInterfaceDeclaration`.

Sometimes, we want to declare interfaces on instances, even though
those instances get interfaces from their classes.  Suppose we create
a new interface, `ISpecial`::

  >>> class ISpecial(zope.interface.Interface):
  ...     reason = zope.interface.Attribute("Reason why we're special")
  ...     def brag():
  ...         "Brag about being special"

We can make a an existing foo instance special by providing `reason`
and `brag` attributes::

  >>> foo.reason = 'I just am'
  >>> def brag():
  ...      return "I'm special!"
  >>> foo.brag = brag
  >>> foo.reason
  'I just am'
  >>> foo.brag()
  "I'm special!"

and by declaring the interface::

  >>> zope.interface.directlyProvides(foo, ISpecial)

then the new interface is included in the provided interfaces::

  >>> ISpecial.providedBy(foo)
  True
  >>> list(zope.interface.providedBy(foo))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

We can find out what interfaces are directly provided by an object::

  >>> list(zope.interface.directlyProvidedBy(foo))
  [<InterfaceClass __main__.ISpecial>]

  >>> newfoo = Foo()
  >>> list(zope.interface.directlyProvidedBy(newfoo))
  []

Inherited declarations
----------------------

Normally, declarations are inherited::

  >>> class SpecialFoo(Foo):
  ...     zope.interface.implements(ISpecial)
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

  >>> list(zope.interface.implementedBy(SpecialFoo))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

  >>> list(zope.interface.providedBy(SpecialFoo()))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

Sometimes, you don't want to inherit declarations.  In that case, you
can use `implementsOnly`, instead of `implements`::

  >>> class Special(Foo):
  ...     zope.interface.implementsOnly(ISpecial)
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

  >>> list(zope.interface.implementedBy(Special))
  [<InterfaceClass __main__.ISpecial>]

  >>> list(zope.interface.providedBy(Special()))
  [<InterfaceClass __main__.ISpecial>]

External declarations
---------------------

Normally, we make implementation declarations as part of a class
definition. Sometimes, we may want to make declarations from outside
the class definition. For example, we might want to declare interfaces
for classes that we didn't write.  The function `classImplements` can
be used for this purpose::

  >>> class C:
  ...     pass

  >>> zope.interface.classImplements(C, IFoo)
  >>> list(zope.interface.implementedBy(C))
  [<InterfaceClass __main__.IFoo>]

We can use `classImplementsOnly` to exclude inherited interfaces::

  >>> class C(Foo):
  ...     pass

  >>> zope.interface.classImplementsOnly(C, ISpecial)
  >>> list(zope.interface.implementedBy(C))
  [<InterfaceClass __main__.ISpecial>]



Declaration Objects
-------------------

When we declare interfaces, we create *declaration* objects.  When we
query declarations, declaration objects are returned::

  >>> type(zope.interface.implementedBy(Special))
  <class 'zope.interface.declarations.Implements'>

Declaration objects and interface objects are similar in many ways. In
fact, they share a common base class.  The important thing to realize
about them is that they can be used where interfaces are expected in
declarations. Here's a silly example::

  >>> class Special2(Foo):
  ...     zope.interface.implementsOnly(
  ...          zope.interface.implementedBy(Foo),
  ...          ISpecial,
  ...          )
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

The declaration here is almost the same as
``zope.interface.implements(ISpecial)``, except that the order of
interfaces in the resulting declaration is different::

  >>> list(zope.interface.implementedBy(Special2))
  [<InterfaceClass __main__.IFoo>, <InterfaceClass __main__.ISpecial>]


Interface Inheritance
=====================

Interfaces can extend other interfaces. They do this simply by listing
the other interfaces as base interfaces::

  >>> class IBlat(zope.interface.Interface):
  ...     """Blat blah blah"""
  ...
  ...     y = zope.interface.Attribute("y blah blah")
  ...     def eek():
  ...         """eek blah blah"""

  >>> IBlat.__bases__
  (<InterfaceClass zope.interface.Interface>,)

  >>> class IBaz(IFoo, IBlat):
  ...     """Baz blah"""
  ...     def eek(a=1):
  ...         """eek in baz blah"""
  ...

  >>> IBaz.__bases__
  (<InterfaceClass __main__.IFoo>, <InterfaceClass __main__.IBlat>)

  >>> names = list(IBaz)
  >>> names.sort()
  >>> names
  ['bar', 'eek', 'x', 'y']

Note that `IBaz` overrides eek::

  >>> IBlat['eek'].__doc__
  'eek blah blah'
  >>> IBaz['eek'].__doc__
  'eek in baz blah'

We were careful to override eek in a compatible way.  When an
extending an interface, the extending interface should be compatible
[#compat]_ with the extended interfaces.

We can ask whether one interface extends another::

  >>> IBaz.extends(IFoo)
  True
  >>> IBlat.extends(IFoo)
  False

Note that interfaces don't extend themselves::

  >>> IBaz.extends(IBaz)
  False

Sometimes we wish they did, but we can, instead use `isOrExtends`::

  >>> IBaz.isOrExtends(IBaz)
  True
  >>> IBaz.isOrExtends(IFoo)
  True
  >>> IFoo.isOrExtends(IBaz)
  False

When we iterate over an interface, we get all of the names it defines,
including names defined by base interfaces. Sometimes, we want *just*
the names defined by the interface directly. We bane use the `names`
method for that::

  >>> list(IBaz.names())
  ['eek']

Inheritance if attribute specifications
---------------------------------------

An interface may override attribute definitions from base interfaces.
If two base interfaces define the same attribute, the attribute is
inherited from the most specific interface. For example, with:

  >>> class IBase(zope.interface.Interface):
  ...
  ...     def foo():
  ...         "base foo doc"

  >>> class IBase1(IBase):
  ...     pass

  >>> class IBase2(IBase):
  ...
  ...     def foo():
  ...         "base2 foo doc"

  >>> class ISub(IBase1, IBase2):
  ...     pass

ISub's definition of foo is the one from IBase2, since IBase2 is more
specific that IBase:

  >>> ISub['foo'].__doc__
  'base2 foo doc'

Note that this differs from a depth-first search.

Sometimes, it's useful to ask whether an interface defines an
attribute directly.  You can use the direct method to get a directly
defined definitions:

  >>> IBase.direct('foo').__doc__
  'base foo doc'

  >>> ISub.direct('foo')

Specifications
--------------

Interfaces and declarations are both special cases of specifications.
What we described above for interface inheritence applies to both
declarations and specifications.  Declarations actually extend the
interfaces that they declare:

  >>> class Baz:
  ...     zope.interface.implements(IBaz)

  >>> baz_implements = zope.interface.implementedBy(Baz)
  >>> baz_implements.__bases__
  (<InterfaceClass __main__.IBaz>,)

  >>> baz_implements.extends(IFoo)
  True

  >>> baz_implements.isOrExtends(IFoo)
  True
  >>> baz_implements.isOrExtends(baz_implements)
  True

Specifications (interfaces and declarations) provide an `__sro__`
that lists the specification and all of it's ancestors:

  >>> baz_implements.__sro__
  (<implementedBy __main__.Baz>,
   <InterfaceClass __main__.IBaz>,
   <InterfaceClass __main__.IFoo>,
   <InterfaceClass __main__.IBlat>,
   <InterfaceClass zope.interface.Interface>)


Tagged Values
=============

Interfaces and attribute descriptions support an extension mechanism,
borrowed from UML, called "tagged values" that lets us store extra
data::

  >>> IFoo.setTaggedValue('date-modified', '2004-04-01')
  >>> IFoo.setTaggedValue('author', 'Jim Fulton')
  >>> IFoo.getTaggedValue('date-modified')
  '2004-04-01'
  >>> IFoo.queryTaggedValue('date-modified')
  '2004-04-01'
  >>> IFoo.queryTaggedValue('datemodified')
  >>> tags = list(IFoo.getTaggedValueTags())
  >>> tags.sort()
  >>> tags
  ['author', 'date-modified']

Function attributes are converted to tagged values when method
attribute definitions are created::

  >>> class IBazFactory(zope.interface.Interface):
  ...     def __call__():
  ...         "create one"
  ...     __call__.return_type = IBaz

  >>> IBazFactory['__call__'].getTaggedValue('return_type')
  <InterfaceClass __main__.IBaz>


Invariants
==========

Interfaces can express conditions that must hold for objects that
provide them. These conditions are expressed using one or more
invariants.  Invariants are callable objects that will be called with
an object that provides an interface. An invariant raises an `Invalid`
exception if the condition doesn't hold.  Here's an example::

  >>> class RangeError(zope.interface.Invalid):
  ...     """A range has invalid limits"""
  ...     def __repr__(self):
  ...         return "RangeError(%r)" % self.args

  >>> def range_invariant(ob):
  ...     if ob.max < ob.min:
  ...         raise RangeError(ob)

Given this invariant, we can use it in an interface definition::

  >>> class IRange(zope.interface.Interface):
  ...     min = zope.interface.Attribute("Lower bound")
  ...     max = zope.interface.Attribute("Upper bound")
  ...
  ...     zope.interface.invariant(range_invariant)

Interfaces have a method for checking their invariants::

  >>> class Range(object):
  ...     zope.interface.implements(IRange)
  ...
  ...     def __init__(self, min, max):
  ...         self.min, self.max = min, max
  ...
  ...     def __repr__(self):
  ...         return "Range(%s, %s)" % (self.min, self.max)

  >>> IRange.validateInvariants(Range(1,2))
  >>> IRange.validateInvariants(Range(1,1))
  >>> IRange.validateInvariants(Range(2,1))
  Traceback (most recent call last):
  ...
  RangeError: Range(2, 1)

If you have multiple invariants, you may not want to stop checking
after the first error.  If you pass a list to `validateInvariants`,
then a single `Invalid` exception will be raised with the list of
exceptions as it's argument::

  >>> errors = []
  >>> IRange.validateInvariants(Range(2,1), errors)
  Traceback (most recent call last):
  ...
  Invalid: [RangeError(Range(2, 1))]

And the list will be filled with the individual exceptions::

  >>> errors
  [RangeError(Range(2, 1))]


  >>> del errors[:]




.. [#create] The main reason we subclass `Interface` is to cause the
             Python class statement to create an interface, rather
             than a class.

             It's possible to create interfaces by calling a special
             interface class directly.  Doing this, it's possible
             (and, on rare occasions, useful) to create interfaces
             that don't descend from `Interface`.  Using this
             technique is beyond the scope of this document.

.. [#factory] Classes are factories.  They can be called to create
              their instances.  We expect that we will eventually
              extend the concept of implementation to other kinds of
              factories, so that we can declare the interfaces
              provided by the objects created.

.. [#compat] The goal is substitutability.  An object that provides an
             extending interface should be substitutable for an object
             that provides the extended interface.  In our example, an
             object that provides IBaz should be usable whereever an
             object that provides IBlat is expected.

             The interface implementation doesn't enforce this.
             but maybe it should do some checks.
