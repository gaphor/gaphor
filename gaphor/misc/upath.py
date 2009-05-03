"""
This module contains some support code for queries on lists.
"""

def match(element, expr):
    """
    Returns True if the expression returns True. The context for the expression
    is the element.


    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can create a path for each object:

    >>> a = A('root')
    >>> a.a = A('level1')
    >>> a.b = A('b')
    >>> a.a.text = 'help'
    >>> match(a, 'name=="root"')
    True
    >>> match(a, 'b.name=="b"')
    True
    >>> match(a, 'name=="blah"')
    False
    >>> match(a, 'nonexistent=="root"')
    False

    """
    d = dict()
    d.update(element.__class__.__dict__)
    d.update(element.__dict__)

    try:
        return eval(expr, d)
    except NameError:
        # attribute does not (yet) exist
        return False


class Matcher(object):

    def __init__(self, expr):
        self.expr = expr

    def __call__(self, element):
        return match(element, self.expr)


class MList(list):
    """
    Things get nicer if we implement this in __getitem__ for example:

    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can do nice things with this list:

    >>> m = MList()
    >>> m.append(A('one'))
    >>> m.append(A('two'))
    >>> m.append(A('three'))
    >>> m[1].name
    'two'
    >>> m['name=="one"'] # doctest: +ELLIPSIS
    [<__main__.A object at 0x...>]
    >>> m['name=="two"', 0].name
    'two'
    """

    def __getitem__(self, key):
        try:
            # See if the list can deal with it (don't change default behaviour)
            return super(MList, self).__getitem__(key)
        except TypeError:
            # Nope, try our matcher trick
            if type(key) is tuple:
                key, remainder = key[0], key[1:]
            else:
                remainder = None

            matcher = Matcher(key)
            matched = filter(matcher, self)
            if remainder:
                return MList(matched).__getitem__(*remainder)
            else:
                return MList(matched)


import doctest
doctest.testmod()
# vim: sw=4:et:ai
