# vim:sw=4:et
"""Attribute item.
"""

import gobject
import diacanvas
from gaphor.diagram import initialize_item

from feature import FeatureItem

class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

initialize_item(AttributeItem)
#gobject.type_register(AttributeItem)
#diacanvas.set_callbacks(AttributeItem)
