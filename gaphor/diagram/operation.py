# vim:sw=4:et
"""Operation item.
"""

import gobject
import diacanvas
from feature import FeatureItem

class OperationItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

gobject.type_register(OperationItem)
diacanvas.set_callbacks(OperationItem)
