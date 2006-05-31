===============
Deprecation API
===============

When we started working on Zope 3.1, we noticed that the hardest part of the
development process was to ensure backward-compatibility and correctly mark
deprecated modules, classes, functions, methods and properties. This module
provides a simple function called `deprecated(names, reason)` to deprecate the
previously mentioned Python objects.

Let's start with a demonstration of deprecating any name inside a module. To
demonstrate the functionality, I have placed the following code inside the
`tests.py` file of this package:

  from zope.deprecation import deprecated
  demo1 = 1
  deprecated('demo1', 'demo1 is no more.')

  demo2 = 2
  deprecated('demo2', 'demo2 is no more.')

  demo3 = 3
  deprecated('demo3', 'demo3 is no more.')

The first argument to the `deprecated()` function is a list of names that
should be declared deprecated. If the first argument is a string, it is
interpreted as one name. The second argument is the reason the particular name
has been deprecated. It is good practice to also list the version in which the
name will be removed completely.

Let's now see how the deprecation warnings are displayed.

  >>> from zope.deprecation import tests
  >>> tests.demo1
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: demo1: demo1 is no more.
  ...
  1

  >>> import zope.deprecation.tests
  >>> zope.deprecation.tests.demo2
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: demo2: demo2 is no more.
  ...
  2

You can see that merely importing the affected module or one of its parents
does not cause a deprecation warning. Only when we try to access the name in
the module, we get a deprecation warning. On the other hand, if we import the
name directly, the deprecation warning will be raised immediately.

  >>> from zope.deprecation.tests import demo3
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: demo3: demo3 is no more.
  ...

Also, once a deprecation warning has been displayed, it is not shown again:

  >>> from zope.deprecation import tests
  >>> tests.demo1
  1

New let's see how properties and methods can be deprecated. We are going to
use the same function as before, except that this time, we do not pass in names
as first argument, but the method or attribute itself. The function then
returns a wrapper that sends out a deprecation warning when the attribute or
method is accessed.

  >>> from zope.deprecation import deprecation
  >>> class MyComponent(object):
  ...     foo = property(lambda self: 1)
  ...     foo = deprecation.deprecated(foo, 'foo is no more.')
  ...
  ...     bar = 2
  ...
  ...     def blah(self):
  ...         return 3
  ...     blah = deprecation.deprecated(blah, 'blah() is no more.')
  ...
  ...     def splat(self):
  ...         return 4

And here is the result:

  >>> my = MyComponent()
  >>> my.foo
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: foo is no more.
  ...
  1
  >>> my.bar
  2
  >>> my.blah()
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: blah() is no more.
  ...
  3
  >>> my.splat()
  4


Temporarily Turning Off Deprecation Warnings
--------------------------------------------

In some cases it is desireable to turn off the deprecation warnings for a
short time. To support such a feature, the `zope.deprecation` package provides
an attribute called `__show__`. One can ask for its status by calling it:

  >>> from zope.deprecation import __show__
  >>> __show__()
  True

  >>> class Foo(object):
  ...     bar = property(lambda self: 1)
  ...     bar = deprecation.deprecated(bar, 'bar is no more.')
  ...     blah = property(lambda self: 1)
  ...     blah = deprecation.deprecated(blah, 'blah is no more.')
  >>> foo = Foo()

  >>> foo.bar
  From tests.py's showwarning():
  ...README.txt:1: DeprecationWarning: bar is no more.
  ...
  1

You can turn off the depraction warnings using

  >>> __show__.off()
  >>> __show__()
  False

  >>> foo.blah
  1

Now, you can also nest several turn-offs, so that calling `off()` multiple
times is meaningful:

  >>> __show__.stack
  [False]

  >>> __show__.off()
  >>> __show__.stack
  [False, False]

  >>> __show__.on()
  >>> __show__.stack
  [False]
  >>> __show__()
  False

  >>> __show__.on()
  >>> __show__.stack
  []
  >>> __show__()
  True

You can also reset `__show__` to `True`:

  >>> __show__.off()
  >>> __show__.off()
  >>> __show__()
  False

  >>> __show__.reset()
  >>> __show__()
  True

Finally, you cannot call `on()` without having called `off()` before:

  >>> __show__.on()
  Traceback (most recent call last):
  ...
  IndexError: pop from empty list
