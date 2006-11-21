"""
ipair function
"""

def ipair(l):
    """
    This module contains a small utility function that can be used to iterate
    over a list of items, each item is returned with it's next item.

    >>> for a, b in ipair((1,2,3,4,5,6)):
    ...     print a, b
    1 2
    2 3
    3 4
    4 5
    5 6
    """
    i1 = iter(l)
    i2 = iter(l)
    i2.next()
    while 1:
        yield i1.next(), i2.next()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
