# vim:sw=4:et
"""Attribute item.
"""

import gobject
import diacanvas
from feature import FeatureItem

class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

gobject.type_register(AttributeItem)
diacanvas.set_callbacks(AttributeItem)
