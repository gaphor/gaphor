def ipair(l):
    """
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

import doctest
doctest.testmod()
