"""
Interfaces related to the user interface.
"""


class _PropertyPages:
    def __init__(self):
        self.pages = []

    def register(self, subject_type):
        def reg(func):
            self.pages.append((subject_type, func))
            return func

        return reg

    def __call__(self, subject):
        for subject_type, func in self.pages:
            if isinstance(subject, subject_type):
                yield func(subject)


PropertyPages = _PropertyPages()
