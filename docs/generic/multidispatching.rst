Multidispatching
================

Multidispatching allows you to define methods and functions which should behave
differently based on arguments' types without cluttering ``if-elif-else`` chains
and ``isinstance`` calls.

All you need is inside ``generic.multidispatch`` module. See examples below to
learn how to use it to define multifunctions and multimethods.

.. contents::
   :local:

Multifunctions
--------------

Suppose we want to define a function which behaves differently based on
arguments' types. The naive solution is to inspect argument types with
``isinstance`` function calls but generic provides us with ``@multidispatch``
decorator which can easily reduce the amount of boilerplate and provide
desired level of extensibility::

  from generic.multidispatching import multidispatch

  @multidispatch(Dog)
  def sound(o):
    print "Woof!"

  @sound.when(Cat)
  def sound(o):
    print "Meow!"

Each separate definition of ``sound`` function works for different argument
types, we will call each such definition *a multidispatch case* or simply *a
case*. We can test if our ``sound`` multidispatch works as expected::

  >>> sound(Dog())
  Woof!
  >>> sound(Cat())
  Meow!
  >>> sound(Duck())
  Traceback
  ...
  TypeError

The main advantage of using multifunctions over single function with a bunch of
``isinstance`` checks is extensibility -- you can add more cases for other types
even in separate module::

  from somemodule import sound

  @sound.when
  def sound(o)
    print "Quack!"

When behaviour of multidispatch depends on some argument we will say that this
multidispatch *dispatches* on this argument.

Multifunctions of several arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also define multifunctions of several arguments and even decide on which
of first arguments you want to dispatch. For example the following function will
only dispatch on its first argument while requiring both of them::

  @multidispatch(Dog)
  def walk(dog, meters):
    print "Dog walks for %d meters" % meters

But sometimes you want multifunctions to dispatch on more than one argument,
then you just have to provide several arguments to ``multidispatch`` decorator
and to subsequent ``when`` decorators::

  @multidispatch(Dog, Cat)
  def chases(dog, cat):
    return True

  @chases.when(Dog, Dog)
  def chases(dog, dog):
    return None

  @chases.when(Cat, Dog)
  def chases(cat, dog):
    return False

You can have any number of arguments to dispatch on but they should be all
positional, keyword arguments are allowed for multifunctions only if they're not
used for dispatch.


API reference
-------------

.. autofunction:: gaphor.misc.generic.multidispatch.multidispatch

.. autoclass:: gaphor.misc.generic.multidispatch.FunctionDispatcher
   :members: register

