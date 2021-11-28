"""The Coder.

The idea:
* Get all classes from a model
  * Drop all classes declared in a Profile
  * Drop all classes from a package blacklist
  * Drop all classes derived from SimpleAttribute's
  * Order all classes in hierarchical order
* Write class definitions
* Write attributes, derived unions, associations, redefines, etc.
  (not sure if there should be an order)

Notes:
* Enumerations are classes ending with "Kind"
* Two stereotypes: Tagged and SimpleAttribute
"""
from gaphor import UML


class Coder:
    def __init__(self, class_):
        self._class = class_

    def __str__(self):
        return f"class {self._class.name}:"

    def __iter__(self):
        if self._class.attribute:
            for attr in sorted(self._class.attribute, key=lambda a: a.name or ""):
                if attr.association:
                    yield f"{attr.name}: relation_{'one' if attr.upper == '1' else 'many'}[{attr.type.name}]"
                else:
                    yield f"{attr.name}: attribute[{attr.typeValue}]"
        else:
            yield "pass"


def super_classes(c: UML.Class):
    for g in c.generalization:
        yield g.general
        yield from super_classes(g.general)


def is_enumeration(c: UML.Class) -> bool:
    return bool(c.name and c.name.endswith("Kind"))


def is_simple_attribute(c: UML.Class) -> bool:
    for s in UML.model.get_applied_stereotypes(c):
        if s.name == "SimpleAttribute":
            return True
    for g in c.generalization:
        if is_simple_attribute(g.general):
            return True
    return False


def is_profile_class(c: UML.Class):
    ...


def is_in_toplevel_package(c: UML.Class, package_name: str):
    ...
