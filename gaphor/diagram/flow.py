'''
ControlFlow and ObjectFlow -- 
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from diagramitem import DiagramItem

import relationship

class FlowItem(relationship.RelationshipItem):

    def __init__(self, id=None):
        relationship.RelationshipItem.__init__(self, id)
        self.set(has_tail=1, tail_fill_color=0,
                 tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)
        
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        for edge in head_subject.incoming:
            #print 'supplier', supplier, supplier.client, tail_subject
            if tail_subject is edge.target:
                # Check if the dependency is not already in our diagram
                for item in self.subject.presentation:
                    if item.canvas is self.canvas and item is not self:
                        break
                else:
                    return edge

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.ActivityNode)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                relation = gaphor.resource(UML.ElementFactory).create(UML.ControlFlow)
                relation.source = s1
                relation.target = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        if self.subject:
            del self.subject


class FlowGuard(diacanvas.CanvasItem, diacanvas.CanvasEditable, DiagramItem):

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        self.set_flags(diacanvas.COMPOSITE)
        
        font = pango.FontDescription(AssociationEnd.FONT)
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(font)
        self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)
        self._name_border = diacanvas.shape.Path()
        self._name_border.set_color(diacanvas.color(128,128,128))
        self._name_border.set_line_width(1.0)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def postload(self):
        DiagramItem.postload(self)

    # Editable

    def on_editable_start_editing(self, shape):
        if shape == self._name:
            log.info('editing name')
        elif shape == self._mult:
            log.info('editing mult')
        #self.preserve_property('name')

    def on_editable_editing_done(self, shape, new_text):
        if shape in (self._name, self._mult):
            if self.subject and (shape == self._name or new_text != ''):
                self.subject.parse(new_text)
            self.set_text()
            log.info('editing done')

initialize_item(FlowItem, UML.ControlFlow)
initialize_item(FlowGuard)

