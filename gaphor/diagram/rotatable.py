import gobject
import diacanvas

# item direction
NORTH, EAST, SOUTH, WEST = range(4)

# dia handle direction to item direction mapping
dh2dir = {
    diacanvas.HANDLE_N: NORTH,
    diacanvas.HANDLE_E: EAST,
    diacanvas.HANDLE_S: SOUTH,
    diacanvas.HANDLE_W: WEST,
}

# item direction to dia handle direction mapping
dir2dh = dict((y, x) for x, y in dh2dir.items())

xdirsign = {
    NORTH:  0,
    EAST:  -1,
    SOUTH:  0,
    WEST:   1,
}

ydirsign = {
    NORTH:  1,
    EAST:   0,
    SOUTH: -1,
    WEST:   0,
}

dirside = {
    NORTH:  SOUTH,
    EAST:   WEST,
    SOUTH:  NORTH,
    WEST:   EAST,
}

class SimpleRotation:
    """
    Object which supports simple rotation. Simple rotation is rotating
    object by one step (90 degrees).
    """

    __gproperties__ = {
        'dir': (gobject.TYPE_INT, 'direction', 'direction of an object',
                NORTH, WEST, WEST, gobject.PARAM_READWRITE),
    }

    def __init__(self, id):
        self._dir = WEST
        self.set_prop_persistent('dir')


    def rotate(self, step = 1):
        """
        Rotate by given amount of steps.
        """
        self.props.dir = abs((self.props.dir + step) % 4)
        assert 0 <= self.props.dir < 4


    def do_set_property(self, pspec, value):
        if pspec.name == 'dir':
            self._dir = value


    def do_get_property(self, pspec):
        if pspec.name == 'dir':
            return self._dir
        else:
            return None
