##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Adapter registry tests

$Id$
"""
import unittest
import zope.interface
from zope.interface.adapter import AdapterRegistry
import zope.interface

class IF0(zope.interface.Interface):
    pass
class IF1(IF0):
    pass

class IB0(zope.interface.Interface):
    pass
class IB1(IB0):
    pass

class IR0(zope.interface.Interface):
    pass
class IR1(IR0):
    pass


def test_orderwith():
    """
    >>> Interface = zope.interface.Interface
    >>> bywith = {(Interface, Interface): 'A0',
    ...           (IF0,       Interface): 'A1', 
    ...           (Interface, IB0):       'A2', 
    ...           (IF0,       IB0):       'A3', 
    ...           (IF1,       IB0):       'A4', 
    ...           (IF0,       IB1):       'A5', 
    ...           (IF1,       IB1):       'A6', 
    ...          }

    >>> [value for spec, value in zope.interface.adapter.orderwith(bywith)]
    ['A6', 'A4', 'A5', 'A3', 'A1', 'A2', 'A0']
    """


def test_multi_adapter_get_best_match():
    """
    >>> registry = AdapterRegistry()

    >>> class IB2(IB0):
    ...     pass
    >>> class IB3(IB2, IB1):
    ...     pass
    >>> class IB4(IB1, IB2):
    ...     pass

    >>> registry.register([None, IB1], IR0, '', 'A1')
    >>> registry.register([None, IB0], IR0, '', 'A0')
    >>> registry.register([None, IB2], IR0, '', 'A2')

    >>> registry.lookup((IF1, IB1), IR0, '')
    'A1'
    >>> registry.lookup((IF1, IB2), IR0, '')
    'A2'
    >>> registry.lookup((IF1, IB0), IR0, '')
    'A0'
    >>> registry.lookup((IF1, IB3), IR0, '')
    'A2'
    >>> registry.lookup((IF1, IB4), IR0, '')
    'A1'
    """

def test_multi_adapter_lookupAll_get_best_matches():
    """
    >>> registry = AdapterRegistry()

    >>> class IB2(IB0):
    ...     pass
    >>> class IB3(IB2, IB1):
    ...     pass
    >>> class IB4(IB1, IB2):
    ...     pass

    >>> registry.register([None, IB1], IR0, '', 'A1')
    >>> registry.register([None, IB0], IR0, '', 'A0')
    >>> registry.register([None, IB2], IR0, '', 'A2')

    >>> registry.lookupAll((IF1, IB1), IR0).next()[1]
    'A1'
    >>> registry.lookupAll((IF1, IB2), IR0).next()[1]
    'A2'
    >>> registry.lookupAll((IF1, IB0), IR0).next()[1]
    'A0'
    >>> registry.lookupAll((IF1, IB3), IR0).next()[1]
    'A2'
    >>> registry.lookupAll((IF1, IB4), IR0).next()[1]
    'A1'
    """


def test_multi_adapter_w_default():
    """
    >>> registry = AdapterRegistry()
    
    >>> registry.register([None, None], IB1, 'bob', 'A0')

    >>> registry.lookup((IF1, IR1), IB0, 'bob')
    'A0'
    
    >>> registry.register([None, IR0], IB1, 'bob', 'A1')

    >>> registry.lookup((IF1, IR1), IB0, 'bob')
    'A1'
    
    >>> registry.lookup((IF1, IR1), IB0, 'bruce')

    >>> registry.register([None, IR1], IB1, 'bob', 'A2')
    >>> registry.lookup((IF1, IR1), IB0, 'bob')
    'A2'
    """

def test_multi_adapter_w_inherited_and_multiple_registrations():
    """
    >>> registry = AdapterRegistry()

    >>> class IX(zope.interface.Interface):
    ...    pass

    >>> registry.register([IF0, IR0], IB1, 'bob', 'A1')
    >>> registry.register([IF1, IX], IB1, 'bob', 'AX')

    >>> registry.lookup((IF1, IR1), IB0, 'bob')
    'A1'
    """

def test_named_adapter_with_default():
    """Query a named simple adapter

    >>> registry = AdapterRegistry()

    If we ask for a named adapter, we won't get a result unless there
    is a named adapter, even if the object implements the interface:

    >>> registry.lookup([IF1], IF0, 'bob')

    >>> registry.register([None], IB1, 'bob', 'A1')
    >>> registry.lookup([IF1], IB0, 'bob')
    'A1'

    >>> registry.lookup([IF1], IB0, 'bruce')

    >>> registry.register([None], IB0, 'bob', 'A2')
    >>> registry.lookup([IF1], IB0, 'bob')
    'A2'
    """

def test_multi_adapter_gets_closest_provided():
    """
    >>> registry = AdapterRegistry()
    >>> registry.register([IF1, IR0], IB0, 'bob', 'A1')
    >>> registry.register((IF1, IR0), IB1, 'bob', 'A2')
    >>> registry.lookup((IF1, IR1), IB0, 'bob')
    'A1'

    >>> registry = AdapterRegistry()
    >>> registry.register([IF1, IR0], IB1, 'bob', 'A2')
    >>> registry.register([IF1, IR0], IB0, 'bob', 'A1')
    >>> registry.lookup([IF1, IR0], IB0, 'bob')
    'A1'

    >>> registry = AdapterRegistry()
    >>> registry.register([IF1, IR0], IB0, 'bob', 'A1')
    >>> registry.register([IF1, IR1], IB1, 'bob', 'A2')
    >>> registry.lookup([IF1, IR1], IB0, 'bob')
    'A2'

    >>> registry = AdapterRegistry()
    >>> registry.register([IF1, IR1], IB1, 'bob', 2)
    >>> registry.register([IF1, IR0], IB0, 'bob', 1)
    >>> registry.lookup([IF1, IR1], IB0, 'bob')
    2
    """

def test_multi_adapter_check_non_default_dont_hide_default():
    """
    >>> registry = AdapterRegistry()

    >>> class IX(zope.interface.Interface):
    ...     pass

    
    >>> registry.register([None, IR0], IB0, 'bob', 1)
    >>> registry.register([IF1,   IX], IB0, 'bob', 2)
    >>> registry.lookup([IF1, IR1], IB0, 'bob')
    1
    """

def test_adapter_hook_with_factory_producing_None():
    """
    >>> registry = AdapterRegistry()
    >>> default = object()
    
    >>> class Object1(object):
    ...     zope.interface.implements(IF0)
    >>> class Object2(object):
    ...     zope.interface.implements(IF0)

    >>> def factory(context):
    ...     if isinstance(context, Object1):
    ...         return 'adapter'
    ...     return None

    >>> registry.register([IF0], IB0, '', factory)

    >>> registry.adapter_hook(IB0, Object1())
    'adapter'
    >>> registry.adapter_hook(IB0, Object2()) is None
    True
    >>> registry.adapter_hook(IB0, Object2(), default=default) is default
    True
    """

def test_adapter_registry_update_upon_interface_bases_change():
    """
    Let's first create a adapter registry and a simple adaptation hook:

    >>> globalRegistry = AdapterRegistry()

    >>> def _hook(iface, ob, lookup=globalRegistry.lookup1):
    ...     factory = lookup(zope.interface.providedBy(ob), iface)
    ...     if factory is None:
    ...         return None
    ...     else:
    ...         return factory(ob)

    >>> zope.interface.interface.adapter_hooks.append(_hook)

    Now we create some interfaces and an implementation:
    
    >>> class IX(zope.interface.Interface):
    ...   pass

    >>> class IY(zope.interface.Interface):
    ...   pass

    >>> class X(object):
    ...  pass

    >>> class Y(object):
    ...  zope.interface.implements(IY)
    ...  def __init__(self, original):
    ...   self.original=original

    and register an adapter:
    
    >>> globalRegistry.register((IX,), IY, '', Y)

    at first, we still expect the adapter lookup from `X` to `IY` to fail:
    
    >>> IY(X()) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt',
                <zope.interface.tests.test_adapter.X object at ...>,
                <InterfaceClass zope.interface.tests.test_adapter.IY>)

    But after we declare an interface on the class `X`, it should pass:

    >>> zope.interface.classImplementsOnly(X, IX)

    >>> IY(X()) #doctest: +ELLIPSIS
    <zope.interface.tests.test_adapter.Y object at ...>

    >>> hook = zope.interface.interface.adapter_hooks.pop()
    """


def test_changing_declarations():
    """

    If we change declarations for a class, those adapter lookup should
    eflect the changes:

    >>> class I1(zope.interface.Interface):
    ...     pass
    >>> class I2(zope.interface.Interface):
    ...     pass

    >>> registry = AdapterRegistry()
    >>> registry.register([I1], I2, '', 42)

    >>> class C:
    ...     pass

    >>> registry.lookup([zope.interface.implementedBy(C)], I2, '')

    >>> zope.interface.classImplements(C, I1)

    >>> registry.lookup([zope.interface.implementedBy(C)], I2, '')
    42
    """


def test_suite():
    from zope.testing import doctest, doctestunit
    return unittest.TestSuite((
        doctestunit.DocFileSuite('../adapter.txt', '../human.txt',
                                 'foodforthought.txt',
                                 globs={'__name__': '__main__'}),
        doctest.DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
