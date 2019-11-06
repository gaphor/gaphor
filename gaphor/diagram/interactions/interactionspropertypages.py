from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional
from gaphor.diagram.propertypages import (
    PropertyPages,
    NamedItemPropertyPage,
    EditableTreeModel,
    create_hbox_label,
    create_tree_view,
    create_uml_combo,
)
from gaphor.diagram.interactions import MessageItem


@PropertyPages.register(MessageItem)
class MessagePropertyPage(NamedItemPropertyPage):
    """Property page for editing message items.

    When message is on communication diagram, then additional messages can
    be added. On sequence diagram sort of message can be changed.
    """

    NAME_LABEL = _("Message")

    MESSAGE_SORT = [
        ("Call", "synchCall"),
        ("Asynchronous", "asynchCall"),
        ("Signal", "asynchSignal"),
        ("Create", "createMessage"),
        ("Delete", "deleteMessage"),
        ("Reply", "reply"),
    ]

    def construct(self):
        page = super().construct()

        item = self.item
        subject = item.subject

        if not subject:
            return page

        if not item.is_communication():
            hbox = create_hbox_label(self, page, _("Message sort"))

            sort_data = self.MESSAGE_SORT
            lifeline = None
            cinfo = item.canvas.get_connection(item.tail)
            if cinfo:
                lifeline = cinfo.connected

            # disallow connecting two delete messages to a lifeline
            if (
                lifeline
                and lifeline.is_destroyed
                and subject.messageSort != "deleteMessage"
            ):
                sort_data = list(sort_data)
                assert sort_data[4][1] == "deleteMessage"
                del sort_data[4]

            combo = self.combo = create_uml_combo(
                sort_data, self._on_message_sort_change
            )
            hbox.pack_start(combo, False, True, 0)

            index = combo.get_model().get_index(subject.messageSort)
            combo.set_active(index)

        return page

    @transactional
    def _on_message_sort_change(self, combo):
        """Update message item's message sort information."""

        combo = self.combo
        ms = combo.get_model().get_value(combo.get_active())

        item = self.item
        subject = item.subject
        lifeline = None
        cinfo = item.canvas.get_connection(item.tail)
        if cinfo:
            lifeline = cinfo.connected

        #
        # allow only one delete message to connect to lifeline's lifetime
        # destroyed status can be changed only by delete message itself
        #
        if lifeline:
            if subject.messageSort == "deleteMessage" or not lifeline.is_destroyed:
                is_destroyed = ms == "deleteMessage"
                lifeline.is_destroyed = is_destroyed
                # TODO: is required here?
                lifeline.request_update()

        subject.messageSort = ms
        # TODO: is required here?
        item.request_update()
