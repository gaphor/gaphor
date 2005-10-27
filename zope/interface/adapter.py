############################################################################
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
############################################################################
"""Adapter-style interface registry

This implementation is based on a notion of "surrogate" interfaces.

$Id$
"""

# Implementation notes

# We keep a collection of surrogates.

# A surrogate is a surrogate for a specification (interface or
# declaration).  We use weak references in order to remove surrogates
# if the corresponding specification goes away.

# Each surrogate keeps track of:

# - The adapters registered directly for that surrogate, and

# - The "implied" adapters, which is the adapters that can be computed
#   from instances of that surrogate.

# The later data structure takes into account adapters registered for
# specifications that the registered surrogate extends.

# The registrations are of the form:

#   {(subscription, with, name, specification) -> factories}

# where:

#   'subscription' is a flag indicating if this registration is for
#   subscription adapters.

#   'with' is a tuple of specs that is non-empty only in the case
#   of multi-adapters.  

#   'name' is a unicode adapter name.  Unnamed adapters have an empty
#   name.

#   'specification' is the interface being adapted to.

#   'factories' is normally a tuple of factories, but can be anything.
#   (See the "raw" option to the query-adapter calls.)  For subscription
#   adapters, it is a tuple of tuples of factories.

# The implied adapters are held in a single dictionary. The items in the
# dictionary are of several forms:

# For single adapters:
#
# {specification -> {name -> object}
#
# where object is usually a sequence of factories

# For multiple adapters:
#
# {(specification, order) -> {name -> {with -> object}}}

# For single subscription adapters:
#
# {('s', specification) -> tuple([object])}

# For multiple-subscription adapters:
#
# {('s', specification, order) -> {with -> tuple([object])}}


from __future__ import generators

import weakref
from zope.interface.ro import ro
from zope.interface.declarations import providedBy
from zope.interface.interface import InterfaceClass, Interface

Default = InterfaceClass("Default", (), {})
Null = InterfaceClass("Null", (), {})

# 2.2 backwards compatability
try:
    enumerate
except NameError:
    def enumerate(l):
        i = 0
        for o in l:
            yield i, o
            i += 1
try:
    basestring
except NameError:
    basestring = (str, unicode)


class ReadProperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self
        return self.func(inst)

class Surrogate(object):
    """Specification surrogate

    A specification surrogate is used to hold adapter registrations on
    behalf of a specification.
    """

    def __init__(self, spec, registry):
        self.spec = spec.weakref()
        self.registry = registry
        spec.subscribe(self)
        self.adapters = {}
        self.dependents = weakref.WeakKeyDictionary()

        self.registry = registry
        self.__bases__ = [registry.get(base) for base in spec.__bases__]
        for base in self.__bases__:
            base.subscribe(self)

    def dirty(self):
        if 'get' in self.__dict__:
            # Not already dirty
            del self.selfImplied
            del self.multImplied
            del self.get

        bases = [self.registry.get(base) for base in self.spec().__bases__]
        if bases != self.__bases__:
            # Our bases changed. unsubscribe from the old ones
            # and subscribe to the new ones
            for base in self.__bases__:
                base.unsubscribe(self)

            self.__bases__ = bases
            for base in bases:
                base.subscribe(self)

        for dependent in self.dependents.keys():
            dependent.dirty()

    def clean(self):
        for base in self.__bases__:
            base.unsubscribe(self)
        self.__bases__ = [self.registry.get(base)
                          for base in self.spec().__bases__]
        for base in self.__bases__:
            base.subscribe(self)

        self.selfImplied, self.multImplied = adapterImplied(self.adapters)

        implied = {}

        ancestors = ro(self)

        # Collect implied data in reverse order to have more specific data
        # override less-specific data.
        ancestors.reverse()
        for ancestor in ancestors:
            
            for key, v in ancestor.selfImplied.iteritems():

                # key is specification or ('s', specification)
                subscription = isinstance(key, tuple) and key[0] == 's'
                if subscription:
                    # v is tuple of subs
                    implied[key] = implied.get(key, ()) + v
                else:
                    oldbyname = implied.get(key)
                    if not oldbyname:
                        implied[key] = oldbyname = {}
                    
                    # v is name -> object
                    oldbyname.update(v)

            for key, v in ancestor.multImplied.iteritems():
                # key is (specification, order)
                #     or ('s', specification, order)
                subscription = key[0] == 's'
                if subscription:
                    oldwithobs = implied.get(key)
                    if not oldwithobs:
                        oldwithobs = implied[key] = {}
                        
                    # v is {with -> tuple([object])}
                    for with, objects in v.iteritems():
                        oldwithobs[with] = oldwithobs.get(with, ()) + objects
                    
                else:
                    oldbyname = implied.get(key)
                    if not oldbyname:
                        implied[key] = oldbyname = {}

                    # v is {name -> {with -> ?}}
                    for name, withobs in v.iteritems():
                        oldwithobs = oldbyname.get(name)
                        if not oldwithobs:
                            oldwithobs = oldbyname[name] = {}

                        # withobs is {with -> object}
                        oldwithobs.update(withobs)

        # Now flatten with mappings to tuples
        for key, v in implied.iteritems():
            if isinstance(key, tuple):
                if key[0] == 's':
                    # subscriptions
                    if isinstance(v, dict):
                        implied[key] = v.items()
                else:
                    byname = v
                    for name, value in byname.iteritems():
                        if isinstance(value, dict):
                            # We have {with -> value}
                            # convert it to sorted [(with, value]
                            byname[name] = orderwith(value)

        self.get = implied.get

    def get(self, key):
        """Get an implied value

        This is only called when the surrogate is dirty
        """
        self.clean()
        return self.__dict__['get'](key)

    def selfImplied(self):
        """Return selfImplied when dirty
        """
        self.clean()
        return self.__dict__['selfImplied']
    selfImplied = ReadProperty(selfImplied)

    def multiImplied(self):
        """Return _multiImplied when dirty
        """
        self.clean()
        return self.__dict__['multiImplied']
    multiImplied = ReadProperty(multiImplied)

    def subscribe(self, dependent):
        self.dependents[dependent] = 1

    def unsubscribe(self, dependent):
        del self.dependents[dependent]

    def _adaptTo(self, specification, object, name='', with=()):
        if object is None:
            try:
                del self.adapters[False, tuple(with), name, specification]
            except KeyError:
                pass
        else:
            self.adapters[False, tuple(with), name, specification
                          ] = object

        self.dirty()

    def _subscriptionAdaptTo(self, specification, object, with=()):
        if object is None:
            raise TypeError, ("Unregistering subscription adapters" 
                              " isn't implemented")

        key = (True, tuple(with), '', specification)
        self.adapters[key] = self.adapters.get(key, ()) + (object, )
        self.dirty()

    def changed(self, which=None):
        self.dirty()

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.spec())

def orderwith(bywith):

    # Convert {with -> adapter} to withs, [(with, value)]
    # such that there are no i, j, i < j, such that
    #           withs[j][0] extends withs[i][0].

    withs = []
    for with, value in bywith.iteritems():
        for i, (w, v) in enumerate(withs):
            if withextends(with, w):
                withs.insert(i, (with, value))
                break
        else:
            withs.append((with, value))
            
    return withs
    

def withextends(with1, with2):
    for spec1, spec2 in zip(with1, with2):
        if spec1.extends(spec2):
            return True
        if spec1 != spec2:
            break
    return False


class AdapterLookup(object):
    # Adapter lookup support
    # We have a class here because we want to provide very
    # fast lookup support in C and making this part of the adapter
    # registry itself would provide problems if someone wanted
    # persistent adapter registries, because we want C slots for fast
    # lookup that would clash with persistence-supplied slots.
    # so this class acts a little bit like a lookup adapter for the adapter
    # registry.

    def __init__(self, registry, surrogates, _remove):
        self._registry = registry
        self._surrogateClass = registry._surrogateClass
        self._default = registry._default
        self._null = registry._null
        self._surrogates = surrogates
        self._remove = _remove

    def lookup(self, required, provided, name='', default=None):
        order = len(required)
        if order == 1:
            # Simple adapter:
            s = self.get(required[0])
            byname = s.get(provided)
            if byname:
                value = byname.get(name)
            else:
                value = None

            if value is None:
                byname = self._default.get(provided)
                if byname:
                    value = byname.get(name, default)
                else:
                    return default
                
            return value

        elif order == 0:
            # null adapter
            byname = self._null.get(provided)
            if byname:
                return byname.get(name, default)
            else:
                return default

        # Multi adapter

        with = required[1:]
        key = provided, order

        for surrogate in self.get(required[0]), self._default:
            byname = surrogate.get(key)
            if not byname:
                continue

            bywith = byname.get(name)
            if not bywith:
                continue

            # Selecting multi-adapters is not just a matter of matching the
            # required interfaces of the adapter to the ones passed. Several
            # adapters might match, but we only want the best one. We use a
            # ranking algorithm to determine the best match.

            # `best` carries the rank and value of the best found adapter.
            best = None
            for rwith, value in bywith:
                # the `rank` describes how well the found adapter matches.
                rank = []
                for rspec, spec in zip(rwith, with):
                    if not spec.isOrExtends(rspec):
                        break # This one is no good
                    # Determine the rank of this particular specification.
                    rank.append(list(spec.__sro__).index(rspec))
                else:
                    # If the new rank is better than the best previously
                    # recorded one, make the new adapter the best one found. 
                    rank = tuple(rank)
                    if best is None or rank < best[0]:
                        best = rank, value
            # If any match was found, return the best one.
            if best:
                return best[1]

        return default

    def lookup1(self, required, provided, name='', default=None):
        return self.lookup((required,), provided, name, default)

    def adapter_hook(self, interface, object, name='', default=None):
        """Hook function used when calling interfaces.

        When called from Interface.__adapt__, only the interface and
        object parameters will be passed.

        If the factory produces `None`, then the default is returned. This
        allows us to prevent adaptation (if desired) and make the factory
        decide whether an adapter will be available.
        """
        factory = self.lookup1(providedBy(object), interface, name)
        if factory is not None:
            adapter = factory(object)
            if adapter is not None:
                return adapter
        return default

    def queryAdapter(self, object, interface, name='', default=None):
        # Note that we rarely call queryAdapter directly
        # We usually end up calling adapter_hook
        return self.adapter_hook(interface, object, name, default)

    def subscriptions(self, required, provided):
        if provided is None:
            provided = Null

        order = len(required)
        if order == 1:
            # Simple subscriptions:
            s = self.get(required[0])
            result = s.get(('s', provided))
            if result:
                result = list(result)
            else:
                result = []

            default = self._default.get(('s', provided))
            if default:
                result.extend(default)
                
            return result

        elif order == 0:
            result = self._null.get(('s', provided))
            if result:
                return list(result)
            else:
                return []
        
        # Multi
        key = 's', provided, order
        with = required[1:]
        result = []
        
        for surrogate in self.get(required[0]), self._default:
            bywith = surrogate.get(key)
            if not bywith:
                continue

            for rwith, values in bywith:
                for rspec, spec in zip(rwith, with):
                    if not spec.isOrExtends(rspec):
                        break # This one is no good
                else:
                    # we didn't break, so we have a match
                    result.extend(values)

        return result

        

    def queryMultiAdapter(self, objects, interface, name='', default=None):
        factory = self.lookup(map(providedBy, objects), interface, name)
        if factory is not None:
            return factory(*objects)

        return default

    def subscribers(self, objects, interface):
        subscriptions = self.subscriptions(map(providedBy, objects), interface)
        subscribers = [subscription(*objects)
                       for subscription in subscriptions]
        # Filter None values
        return [x for x in subscribers if x is not None]

    def get(self, declaration):
        if declaration is None:
            return self._default

        ref = declaration.weakref(self._remove)
        surrogate = self._surrogates.get(ref)
        if surrogate is None:
            surrogate = self._surrogateClass(declaration, self._registry)
            self._surrogates[ref] = surrogate

        return surrogate


class AdapterRegistry(object):
    """Adapter registry
    """

    # Implementation note:
    # We are like a weakref dict ourselves. We can't use a weakref
    # dict because we have to use spec.weakref() rather than
    # weakref.ref(spec) to get weak refs to specs.

    _surrogateClass = Surrogate

    def __init__(self):
        default = self._surrogateClass(Default, self)
        self._default = default
        null = self._surrogateClass(Null, self)
        self._null = null

        # Create separate lookup object and copy it's methods
        surrogates = {Default.weakref(): default, Null.weakref(): null}
        def _remove(k):
            try:
                del surrogates[k]
            except KeyError:
                pass
        lookup = AdapterLookup(self, surrogates, _remove)
        
        for name in ('lookup', 'lookup1', 'queryAdapter', 'get',
                     'adapter_hook', 'subscriptions',
                     'queryMultiAdapter', 'subscribers',
                     ):
            setattr(self, name, getattr(lookup, name))

    def register(self, required, provided, name, value):
        if required:
            with = []
            for iface in required[1:]:
                if iface is None:
                    iface = Interface
                with.append(iface)
            with = tuple(with)
            required = self.get(required[0])
        else:
            with = ()
            required = self._null
        
        if not isinstance(name, basestring):
            raise TypeError("The name provided to provideAdapter "
                            "must be a string or unicode")

        required._adaptTo(provided, value, unicode(name), with)

    def lookupAll(self, required, provided):
        order = len(required)
        if order == 1:
            # Simple adapter:
            s = self.get(required[0])
            byname = s.get(provided)
            if byname:
                for item in byname.iteritems():
                    yield item

            defbyname = self._default.get(provided)
            if defbyname:
                for name, value in defbyname.iteritems():
                    if name in byname:
                        continue
                    yield name, value

            return

        elif order == 0:
            # null adapter
            byname = self._null.get(provided)
            if byname:
                for item in byname.iteritems():
                    yield item

            return


        # Multi adapter

        with = required[1:]
        key = provided, order
        first = ()

        for surrogate in self.get(required[0]), self._default:
            byname = surrogate.get(key)
            if not byname:
                continue

            for name, bywith in byname.iteritems():
                if not bywith or name in first:
                    continue

                # See comments on lookup() above
                best  = None
                for rwith, value in bywith:
                    # the `rank` describes how well the found adapter matches.
                    rank = []
                    for rspec, spec in zip(rwith, with):
                        if not spec.isOrExtends(rspec):
                            break # This one is no good
                        # Determine the rank of this particular specification.
                        rank.append(list(spec.__sro__).index(rspec))
                    else:
                        # If the new rank is better than the best previously
                        # recorded one, make the new adapter the best one found.
                        rank = tuple(rank)
                        if best is None or rank < best[0]:
                            best = rank, value

                # If any match was found, return the best one.
                if best:
                    yield name, best[1]

            first = byname

    def subscribe(self, required, provided, value):
        if required:
            required, with = self.get(required[0]), tuple(required[1:])
        else:
            required = self._null
            with = ()

        if provided is None:
            provided = Null
            
        required._subscriptionAdaptTo(provided, value, with)

def mextends(with, rwith):
    if len(with) == len(rwith):
        for w, r in zip(with, rwith):
            if not w.isOrExtends(r):
                break
        else:
            return True
    return False

def adapterImplied(adapters):
    implied = {}
    multi = {}

    # This dictionary is used to catch situations specific adapters
    # override less specific adapters.
    # Because subscriptions are cumulative, registered doesn't apply.
    registered = {}

    # Add adapters and interfaces directly implied by same:

    for key, value in adapters.iteritems():

        # TODO: Backward compatibility
        # BBB ? Don't need to handle 3-tuples some day
        try:
            (subscription, with, name, target) = key
        except ValueError:
            (with, name, target) = key
            subscription = False

        if subscription:
            if with:
                _add_multi_sub_adapter(with, target, multi, value)
            else:
                _add_named_sub_adapter(target, implied, value)
        else:
            if with:
                _add_multi_adapter(with, name, target, target, multi,
                                   registered, value)
            else:
                _add_named_adapter(target, target, name, implied,
                                   registered, value)

    return implied, multi

def _add_named_adapter(target, provided, name, implied,
                       registered, value):
    
    ikey = target
    rkey = target, name

    byname = implied.get(ikey)
    if not byname:
        byname = implied[ikey] = {}

    if (name not in byname
        or
        (rkey in registered and registered[rkey].extends(provided))
        ):

        registered[rkey] = provided
        byname[name] = value

        for b in target.__bases__:
            _add_named_adapter(b, provided, name, implied,
                               registered, value)

def _add_multi_adapter(with, name, target, provided, implied,
                       registered, object):

    ikey = target, (len(with) + 1)
    byname = implied.get(ikey)
    if not byname:
        byname = implied[ikey] = {}

    bywith = byname.get(name)
    if not bywith:
        bywith = byname[name] = {}

    
    rkey = ikey, name, with # The full key has all 4
    if (with not in bywith
        or
        (rkey not in registered or registered[rkey].extends(provided))
        ):
        # This is either a new entry or it is an entry for a more
        # general interface that is closer provided than what we had
        # before
        registered[rkey] = provided
        bywith[with] = object

    for b in target.__bases__:
        _add_multi_adapter(with, name, b, provided, implied,
                           registered, object)

def _add_named_sub_adapter(target, implied, objects):
    key = ('s', target)
    implied[key] = implied.get(key, ()) + objects
    
    for b in target.__bases__:
        _add_named_sub_adapter(b, implied, objects)

def _add_multi_sub_adapter(with, target, implied, objects):
    key = 's', target, (len(with) + 1)
    bywith = implied.get(key)
    if not bywith:
        bywith = implied[key] = {}

    bywith[with] = bywith.get(with, ()) + objects

    for b in target.__bases__:
        _add_multi_sub_adapter(with, b, implied, objects)
