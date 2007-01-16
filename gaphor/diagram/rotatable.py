import gaphas.item

# item direction
NORTH, EAST, SOUTH, WEST = range(4)

# dia handle direction to item direction mapping
#dh2dir = {
#    Element.NW: NORTH,
#    Element.NE: EAST,
#    diacanvas.HANDLE_S: SOUTH,
#    diacanvas.HANDLE_W: WEST,
#}

# item direction to dia handle direction mapping
#dir2dh = dict((y, x) for x, y in dh2dir.items())

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

    def __init__(self):
        self._dir = WEST
        self.set_prop_persistent('dir')

    
    def rotate(self, step = 1):
        """
        Rotate by given amount of steps.
        """
        self.props.dir = abs((self.props.dir + step) % 4)
        assert 0 <= self.props.dir < 4


    def _set_dir(self, dir):
        self._dir = dir

    dir = property(lambda s: s._dir, _set_dir)

