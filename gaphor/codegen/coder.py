"""The Coder."""


class Coder:
    def __init__(self, class_):
        self._class = class_

    def __str__(self):
        return f"class {self._class.name}:"

    def __iter__(self):
        if self._class.attribute:
            for attr in self._class.attribute:
                yield f"{attr.name}: attribute[{attr.typeValue}]"
        else:
            yield "pass"
