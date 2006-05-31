'''
PackageItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
from gaphor import UML
from nameditem import NamedItem

STEREOTYPE_OPEN = '\xc2\xab' # '<<'
STEREOTYPE_CLOSE = '\xc2\xbb' # '>>'

class PackageItem(NamedItem):

    __uml__ = UML.Package

    TAB_X=50
    TAB_Y=20
    MARGIN_X=60
    MARGIN_Y=30

    FONT_STEREOTYPE='sans 10'

    stereotype_list = []
    popup_menu = NamedItem.popup_menu + (
        'separator',
        'Stereotype', stereotype_list
    )

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

        self._has_stereotype = False
        self._stereotype = diacanvas.shape.Text()
        self._stereotype.set_font_description(pango.FontDescription(self.FONT_STEREOTYPE))
        self._stereotype.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._stereotype.set_markup(False)

    def get_popup_menu(self):
        """In the popup menu a submenu is created with Stereotypes than can be
        applied to this classifier (Class, Interface).
        If the class itself is a metaclass, an option is added to check if the class
        exists.
        """
        subject = self.subject
        stereotype_list = self.stereotype_list
        stereotype_list[:] = []

        from itemactions import ApplyStereotypeAction, register_action
        NamedElement = UML.NamedElement
        Class = UML.Class

        # Find classes that are superclasses of our subject
        mro = filter(lambda e:issubclass(e, NamedElement), type(self.subject).__mro__)
        # Find out their names
        names = map(getattr, mro, ['__name__'] * len(mro))
        # Find stereotypes that extend out metaclass
        classes = self._subject._factory.select(lambda e: e.isKindOf(Class) and e.name in names)

        for class_ in classes:
            for extension in class_.extension:
                stereotype = extension.ownedEnd.type
                stereotype_action = ApplyStereotypeAction(stereotype)
                register_action(stereotype_action, 'ItemFocus')
                stereotype_list.append(stereotype_action.id)
        return NamedItem.get_popup_menu(self)

    def set_stereotype(self, text=None):
        """Set the stereotype text for the diagram item.
        The text, not a Stereotype object.
        @text: text to set.
        """
        if text:
            self._stereotype.set_text(STEREOTYPE_OPEN + text + STEREOTYPE_CLOSE)
            self._has_stereotype = True
        else:
            self._has_stereotype = False
        self.request_update()

    def update_stereotype(self):
        subject = self.subject
        applied_stereotype = subject.appliedStereotype
        if applied_stereotype:
            # Return a nice name to display as stereotype:
            # make first character lowercase unless the second character is uppercase.
            s = ', '.join([s and len(s) > 1 and s[1].isupper() and s \
                           or s and s[0].lower() + s[1:] \
                           or str(s) for s in map(getattr, applied_stereotype, ['name'] * len(applied_stereotype))])
            # Phew!
            self.set_stereotype(s)
        elif isinstance(subject, UML.Profile):
            self.set_stereotype('profile')
        else:
            self.set_stereotype(None)
        self.request_update()

    def on_subject_notify(self, pspec, notifiers=()):
        NamedItem.on_subject_notify(self, pspec, ('appliedStereotype',) + notifiers)
        if self.subject:
            self.update_stereotype()

    def on_subject_notify__appliedStereotype(self, subject, pspec=None):
        if self.subject:
            self.update_stereotype()

    def on_update(self, affine):
        has_stereotype = self._has_stereotype

        st_width = st_height = 0
        if has_stereotype:
            st_width, st_height = self._stereotype.to_pango_layout(True).get_pixel_size()

        # Center the text
        name_width, name_height = self.get_name_size()

        width = max(st_width, name_width)
        height = st_height + name_height

        self.set(min_width=width + PackageItem.MARGIN_X,
                 min_height=height + PackageItem.MARGIN_Y + PackageItem.TAB_Y)

        if has_stereotype:
            self._stereotype.set_pos((0, PackageItem.TAB_Y + PackageItem.MARGIN_Y/2 - st_height))
            self._stereotype.set_max_width(self.width)
            self._stereotype.set_max_height(st_height)

        self.update_name(x=0,
                         y=PackageItem.TAB_Y + PackageItem.MARGIN_Y/2,
                         width=self.width, height=name_height)

        NamedItem.on_update(self, affine)

        o = 0.0
        h = self.height
        w = self.width
        x = PackageItem.TAB_X
        y = PackageItem.TAB_Y
        line = ((x, y), (x, o), (o, o), (o, h), (w, h), (w, y), (o, y))
        self._border.line(line)
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in NamedItem.on_shape_iter(self):
            yield s
        if self._has_stereotype:
            yield self._stereotype
