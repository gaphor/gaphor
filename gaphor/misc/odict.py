# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
from __future__ import absolute_import
from six.moves import map
from six.moves import zip
class odict(dict):

    def __init__(self, dict=()):
        self._keys = []
        super(odict, self).__init__(dict)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        dict.clear(self)
        self._keys = []

    def copy(self):
        dict = dict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return list(zip(self._keys, list(self.values())))

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj=None):
        dict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        dict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return list(map(self.get, self._keys))
    

    def swap(self, k1, k2):
        """
        Swap two elements using their keys.
        """
        i1 = self._keys.index(k1)
        i2 = self._keys.index(k2)
        self._keys[i1], self._keys[i2] = self._keys[i2], self._keys[i1]


    def __iter__(self):
        for k in self._keys:
            yield k
