
from gaphor.UML import *
import gc
import weakref, sys

ef = ElementFactory()

p = ef.create(Parameter)
wp = weakref.ref(p)
assert len(ef.values()) == 1

ef.flush()
del p

gc.collect()

assert wp() is None
assert len(ef.values()) == 0

p = ef.create(Parameter)

assert len(ef.values()) == 1

p.unlink()

assert len(ef.values()) == 0

p = ef.create(Parameter)
l = ef.create(LiteralString)
p.defaultValue = l

assert len(ef.values()) == 2

p.unlink()
del p

assert len(ef.values()) == 0

gc.collect()

