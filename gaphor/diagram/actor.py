'''
ActorItem diagram item
'''
# vim:sw=4

from __future__ import generators

import gobject
import pango
import diacanvas

from gaphor import UML
from gaphor.diagram import initialize_item

from classifier import ClassifierItem

# TODO: add appliedStereotype to actor classifier

class ActorItem(ClassifierItem):
    HEAD=11
    ARM=19
    NECK=10
    BODY=20

    __gproperties__ = {
        'name-width':        (gobject.TYPE_DOUBLE, 'name width',
                         '', 0.0, 10000.0,
                         1, gobject.PARAM_READWRITE),
    }

    DEFAULT_SIZE= {
        'height': (HEAD + NECK + BODY + ARM),
        'width': (ARM * 2),
        'min_height': (HEAD + NECK + BODY + ARM),
        'min_width': (ARM * 2)
    }

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)

        self.drawing_style = self.DRAW_ICON

        self.set(**self.DEFAULT_SIZE)

        # Head
        self._head = diacanvas.shape.Ellipse()
        self._head.set_line_width(2.0)
        # Body
        self._body = diacanvas.shape.Path()
        self._body.set_line_width(2.0)
        # Arm
        self._arms = diacanvas.shape.Path()
        self._arms.set_line_width(2.0)
        # Legs
        self._legs = diacanvas.shape.Path()
        self._legs.set_line_width(2.0)

    def save (self, save_func):
        ClassifierItem.save(self, save_func)
        #self.save_property(save_func, 'name-width')

    def do_set_property (self, pspec, value):
        #print 'Actor: Trying to set property', pspec.name, value
        if pspec.name == 'name-width':
            #self._name.set_property('width', value)
            pass
        else:
            ClassifierItem.do_set_property (self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'name-width':
            #w, h = self.get_name_size()
            return 0.0
        else:
            return ClassifierItem.do_get_property (self, pspec)

    def set_drawing_style(self, style):
        ClassifierItem.set_drawing_style(self, style)
        if self.drawing_style == self.DRAW_ICON:
            self.set(**self.DEFAULT_SIZE)

    # DiaCanvasItem callbacks:

    def update_icon(self, affine):
        """Actors use Icon style, so update it.
        """
        # Center the text (from ClassifierItem):
        w, h = self.get_name_size()
        if w < self.width:
            w = self.width
        self.update_name(x=(self.width - w) / 2, y=self.height,
                         width=w, height=h)

        #ClassifierItem.on_update(self, affine)

        # scaling factors (also compenate the line width):
        fx = self.width / (ActorItem.ARM * 2 + 2);
        fy = self.height / (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM + 2);
        self._head.ellipse((ActorItem.ARM * fx, (ActorItem.HEAD / 2) * fy),
                            ActorItem.HEAD * fx, ActorItem.HEAD * fy)
        self._body.line(((ActorItem.ARM * fx, ActorItem.HEAD * fy),
                         (ActorItem.ARM * fx, (ActorItem.HEAD
                          + ActorItem.NECK + ActorItem.BODY) * fy)))
        self._arms.line(((0, (ActorItem.HEAD + ActorItem.NECK) * fy),
                         (ActorItem.ARM * 2 * fx,
                          (ActorItem.HEAD + ActorItem.NECK) * fy)))
        self._legs.line(((0, (ActorItem.HEAD + ActorItem.NECK
                               + ActorItem.BODY + ActorItem.ARM) * fy),
                          (ActorItem.ARM * fx,
                           (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY) * fy),
                          (ActorItem.ARM * 2 * fx, (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM) * fy)))
        # update the bounding box:
        #ulx, uly, lrx, lry = self.bounds
        #w, h = self._name.get_property('layout').get_pixel_size()
        #if w > self.width:
        #    ulx = (self.width / 2) - (w / 2)
        #    lrx = (self.width / 2) + (w / 2)
        #self.set_bounds ((ulx, uly-1, lrx+1, lry + h))

    def on_update(self, affine):
        ClassifierItem.on_update(self, affine)

        # update the bounding box:
        if self.drawing_style == self.DRAW_ICON:
            w, h = self.get_name_size()
            ulx, uly, lrx, lry = self.bounds
            if w > self.width:
                ulx = (self.width / 2) - (w / 2)
                lrx = (self.width / 2) + (w / 2)
            self.set_bounds ((ulx, uly-1, lrx+1, lry + h))

    def on_shape_iter(self):
        if self.drawing_style == self.DRAW_ICON:
            yield self._head
            yield self._body
            yield self._arms
            yield self._legs
        for s in ClassifierItem.on_shape_iter(self):
            yield s

initialize_item(ActorItem, UML.Actor)
