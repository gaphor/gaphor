# vim:sw=4:et
"""Operation item.
"""

import gobject
import diacanvas
from gaphor.diagram import initialize_item
from feature import FeatureItem

class OperationItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

initialize_item(OperationItem)
