"""
Base code for presentation elements
"""

import ast
import gaphas

from gaphor.UML.uml2 import Element


class Presentation(Element):
    """
    This presentation is used to link the behaviors of `gaphor.UML.Element` and `gaphas.Item`.

    This class should be inherited before the
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        def update(event):
            self.request_update()

        self._watcher = self.watcher(default_handler=update)

        self.watch("subject")

    def watch(self, path, handler=None):
        """
        Watch a certain path of elements starting with the DiagramItem.
        The handler is optional and will default to a simple
        self.request_update().

        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        self._watcher.watch(path, handler)
        return self

    def subscribe_all(self):
        """
        Subscribe all watched paths, as defined through `watch()`.
        """
        self._watcher.subscribe_all()

    def unsubscribe_all(self):
        """
        Subscribe all watched paths, as defined through `watch()`.
        """
        self._watcher.unsubscribe_all()

    def unlink(self):
        """
        Remove the item from the canvas and set subject to None.
        """
        if self.canvas:
            self.canvas.remove(self)
        super().unlink()

    def setup_canvas(self):
        super().setup_canvas()
        self.subscribe_all()

    def teardown_canvas(self):
        self.unsubscribe_all()
        super().teardown_canvas()


class PresentationElement(Presentation, gaphas.Element):
    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        for prop in ("width", "height"):
            save_func(prop, getattr(self, prop))
        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name in ("width", "height"):
            setattr(self, name, ast.literal_eval(value))
        elif name == "show_stereotypes_attrs":
            # TODO: should be handled in storage as an upgrader
            pass
        else:
            super().load(name, value)
