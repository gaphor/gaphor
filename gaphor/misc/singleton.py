class Singleton(type):
    _obj = None
    def __call__(self):
        if self._obj is None:
            self._obj = type.__call__(self)
        return self._obj
