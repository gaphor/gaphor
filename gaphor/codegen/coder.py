"""The Coder."""


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
