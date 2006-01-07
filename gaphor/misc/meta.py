import gobject
import inspect

class GObjectPropsMerge(gobject.GObjectMeta):
    def __new__(cls, name, bases, data):
        if not '__gproperties__' in data:
            props = data['__gproperties__'] = {}
        else:
            props = data['__gproperties__']

        all_bases = set()
        for base in bases:
            all_bases = all_bases.union(set(inspect.getmro(base)))
        for base in all_bases:
            props.update(getattr(base, '__gproperties__', {}))

        return gobject.GObjectMeta.__new__(cls, name, bases, data)


