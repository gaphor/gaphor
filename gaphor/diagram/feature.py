# vim:sw=4:et
'''
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
'''

from modelelement import ModelElementItem
import diacanvas
import pango
import gobject
from diacanvas import CanvasText
from diagramitem import DiagramItem

class FeatureItem(CanvasText, DiagramItem):
    """FeatureItems are model elements who recide inside a ClassItem, such as
    methods and attributes. Those items can have comments attached, but only on
    the left and right side.
    Note that features can also be used inside objects.
    """
    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        #diacanvas.CanvasText.__init__(self)
        font = pango.FontDescription(FeatureItem.FONT)
        self.set(font=font, multiline=False,
                 alignment=pango.ALIGN_LEFT)
        self.set_flags(diacanvas.COMPOSITE)
        w, h = self.get_property('layout').get_pixel_size()
        self.set(height=h)
        self.connect('notify::text', FeatureItem.on_text_notify)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect

    def on_subject_notify(self, pspec):
        DiagramItem.on_subject_notify(self, pspec, ('name',))
        self.set(text=self.subject and self.subject.name or '')

    def on_subject_notify__name(self, subject, pspec):
        self.set(text=self.subject.name)

    def on_text_notify(self, pspec):
        if self.subject and self.text != self.subject.name:
            self.subject.name = self.text
            #self.parent.request_update()

    def on_event(self, event):
        # TODO: handle focus in/out events
        if event.type == diacanvas.EVENT_KEY_PRESS:
            CanvasText.on_event(self, event)
            return True
        else:
            return CanvasText.on_event(self, event)

gobject.type_register(FeatureItem)
diacanvas.set_callbacks(FeatureItem)

