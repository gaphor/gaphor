"""
Metaclass item editors.
"""

from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.propertypages import create_hbox_label, EventWatcher
from gaphor.core import _, transactional
from gaphor.diagram.propertypages import PropertyPages, NamedElementPropertyPage
from gaphor.diagram.classes import ClassItem


def _issubclass(c, b):
    try:
        return issubclass(c, b)
    except TypeError:
        return False


@PropertyPages.register(UML.Class)
class MetaclassNamePropertyPage(NamedElementPropertyPage):
    """
    Metaclass name editor. Provides editable combo box entry with
    predefined list of names of UML classes.
    """

    order = 10

    NAME_LABEL = _("Name")

    CLASSES = list(
        sorted(
            n
            for n in dir(UML)
            if _issubclass(getattr(UML, n), UML.Element) and n != "Stereotype"
        )
    )

    def construct(self):
        if not UML.model.is_metaclass(self.subject):
            return super().construct()

        page = Gtk.VBox()

        subject = self.subject
        if not subject:
            return page

        hbox = create_hbox_label(self, page, self.NAME_LABEL)
        model = Gtk.ListStore(str)
        for c in self.CLASSES:
            model.append([c])

        cb = Gtk.ComboBox.new_with_model_and_entry(model)

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)
        cb.get_child().set_completion(completion)

        entry = cb.get_child()
        entry.set_text(subject and subject.name or "")
        hbox.pack_start(cb, True, True, 0)
        page.default = entry

        # monitor subject.name attribute
        changed_id = entry.connect("changed", self._on_name_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.handler_block(changed_id)
                entry.set_text(event.new_value)
                entry.handler_unblock(changed_id)

        self.watcher.watch("name", handler).register_handlers()
        entry.connect("destroy", self.watcher.unregister_handlers)
        page.show_all()
        return page
