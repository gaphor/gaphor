"""Recursive attribute access functions."""


def rgetattr(obj, attr):
    """
    Get named attribute from an object, i.e. getattr(obj, 'a.a') is
    equivalent to ``obj.a.a''.

     - obj:  object
     - attr: attribute name(s)

    >>> class A: pass
    >>> a = A()
    >>> a.a = A()
    >>> a.a.a = 1
    >>> rgetattr(a, 'a.a')
    1
    >>> rgetattr(a, 'a.c')
    Traceback (most recent call last):
    ...
    AttributeError: 'A' object has no attribute 'c'
    """
    attrs = attr.split(".")
    obj = getattr(obj, attrs[0])
    for name in attrs[1:]:
        obj = getattr(obj, name)
    return obj


def rsetattr(obj, attr, val):
    """
    Set named attribute value on an object, i.e. setattr(obj, 'a.a', 1)
    is equivalent to ``obj.a.a = 1''.

     - obj:  object
     - attr: attribute name(s)
     - val:  attribute value

    >>> class A: pass
    >>> a = A()
    >>> a.a = A()
    >>> a.a.a = 1
    >>> rsetattr(a, 'a.a', 2)
    >>> print(a.a.a)
    2
    >>> rsetattr(a, 'a.c', 3)
    >>> print(a.a.c)
    3
    """
    attrs = attr.split(".")
    if len(attrs) > 1:
        obj = getattr(obj, attrs[0])
        for name in attrs[1:-1]:
            obj = getattr(obj, name)
    setattr(obj, attrs[-1], val)
