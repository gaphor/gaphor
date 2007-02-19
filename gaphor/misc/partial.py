"""
Backport of Python2.5 functools.partial method.

>>> import operator
>>> x = partial(operator.add, 2)
>>> x(3)
5

"""

class partial(object):

    def __init__(*args, **kw):
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)

    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

