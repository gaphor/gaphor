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


# Note: the official documentation is using the terms "Shape" and "Edge" for element and line.


class ElementPresentation(Presentation, gaphas.Element):
    """
    Presentation for Gaphas Element (box-like) items.
    """

    def __init__(self, id=None, model=None, layout=None):
        super().__init__(id, model)
        self.layout = layout

    def pre_update(self, context):
        cr = context.cairo
        self.min_width, self.min_height = self.layout.size(cr)

    def draw(self, context):
        self.layout.draw(context, (0, 0, self.width, self.height))

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


class LinePresentation(Presentation, gaphas.Line):
    def __init__(self, id=None, model=None, layout=None):
        super().__init__(id, model)
        self.layout = layout
        self.fuzziness = 2

    head = property(lambda self: self._handles[0])
    tail = property(lambda self: self._handles[-1])

    def post_update(self, context):
        # nothing to do here, since we do our drawing in separate classes.
        pass

    def draw(self, context):
        self.layout.draw(context, [h.pos for h in self.handles()])

    def save(self, save_func):
        def save_connection(name, handle):
            c = self.canvas.get_connection(handle)
            if c:
                save_func(name, c.connected, reference=True)

        super().save(save_func)
        save_func("matrix", tuple(self.matrix))
        for prop in ("orthogonal", "horizontal"):
            save_func(prop, getattr(self, prop))
        points = [tuple(map(float, h.pos)) for h in self.handles()]
        save_func("points", points)

        save_connection("head-connection", self.head)
        save_connection("tail-connection", self.tail)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "points":
            points = ast.literal_eval(value)
            for x in range(len(points) - 2):
                h = self._create_handle((0, 0))
                self._handles.insert(1, h)
            for i, p in enumerate(points):
                self.handles()[i].pos = p

            # Update connection ports of the line. Only handles are saved
            # in Gaphor file therefore ports need to be recreated after
            # handles information is loaded.
            self._update_ports()

        elif name == "orthogonal":
            self._load_orthogonal = ast.literal_eval(value)
        elif name == "horizontal":
            self.horizontal = ast.literal_eval(value)
        elif name in ("head_connection", "head-connection"):
            self._load_head_connection = value
        elif name in ("tail_connection", "tail-connection"):
            self._load_tail_connection = value
        elif name == "show_stereotypes_attrs":
            # TODO: should be handled in storage as an upgrader
            pass
        else:
            super().load(name, value)

    def postload(self):
        def get_sink(handle, item):

            hpos = self.canvas.get_matrix_i2i(self, item).transform_point(*handle.pos)
            port = None
            dist = 10e6
            for p in item.ports():
                pos, d = p.glue(hpos)
                if not port or d < dist:
                    port = p
                    dist = d

            return gaphas.aspect.ConnectionSink(item, port)

        def postload_connect(handle, item):
            connector = gaphas.aspect.Connector(self, handle)
            sink = get_sink(handle, item)
            connector.connect(sink)

        if hasattr(self, "_load_orthogonal"):
            # Ensure there are enough handles
            if self._load_orthogonal and len(self._handles) < 3:
                p0 = self._handles[-1].pos
                self._handles.insert(1, self._create_handle(p0))
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

        # First update matrix and solve constraints (NE and SW handle are
        # lazy and are resolved by the constraint solver rather than set
        # directly.
        self.canvas.update_matrix(self)
        self.canvas.solver.solve()

        if hasattr(self, "_load_head_connection"):
            postload_connect(self.head, self._load_head_connection)
            del self._load_head_connection

        if hasattr(self, "_load_tail_connection"):
            postload_connect(self.tail, self._load_tail_connection)
            del self._load_tail_connection

        super().postload()
